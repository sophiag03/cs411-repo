from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)

#fixtures
def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


def test_create_meal(mock_cursor):
    """Test creating a new meal in the meals table."""
    
    # Call the function to create a new meal
    create_meal(meal="Meal Name", cuisine="Cuisine Type", price=12.01, difficulty='MED')

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal Name", "Cuisine Type", 12.01, 'MED')
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_duplicate_meal(mock_cursor):
    """Test creating a meal with a duplicate meal name (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Meal with name 'Meal Name' already exists"):
        create_meal(meal="Meal Name", cuisine="Cuisine Type", price=12.01, difficulty='MED')

def test_create_meal_invalid_price():
    """Test error when trying to create a meal with an invalid price (e.g., negative price or non-Integer/non-Float)"""

    # Attempt to create a meal with a negative price
    with pytest.raises(ValueError, match="Invalid price: -12.01. Price must be a positive number."):
        create_meal(meal="Meal Name", cuisine="Cuisine Type", price=-12.01, difficulty='MED')

    # Attempt to create a meal with a non-integer/non-float price
    with pytest.raises(ValueError, match="Invalid price: invalid. Price must be a positive number."):
        create_meal(meal="Meal Name", cuisine="Cuisine Type", price="invalid", difficulty='MED')

def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid difficulty (e.g., not in ['LOW', 'MED', 'HIGH'])."""

    #Attempt to create a meal with a non-string difficulty
    with pytest.raises(ValueError, match="Invalid difficulty level: 10. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Meal Name", cuisine="Cuisine Type", price=12.01, difficulty=10)

    #Attempt to create a meal with a difficulty not in ['LOW', 'MED', 'HIGH']
    with pytest.raises(ValueError, match="Invalid difficulty level: hard. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Meal Name", cuisine="Cuisine Type", price=12.01, difficulty="hard")


def test_clear_meals(mock_cursor, mocker):
    """Test clearing the entire meals table (removes all meals)."""

    # Mock the file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))

    # Call the clear_database function
    clear_meals()

    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')

    # Verify that the correct SQL script was executed
    mock_cursor.executescript.assert_called_once()


def test_delete_song(mock_cursor):
    """Test soft deleting a meal from the meals table by meal ID."""

    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_meal function
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""

    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""

    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)




def test_get_leaderboard_sort_by_wins(mock_cursor):
    """Test the leaderboard for sorting by wins."""
    mock_cursor.fetchall.return_value = [
        (1, 'Pizza', 'Italian', 10.00, 'MED', 10, 6, 0.6),
        (2, 'Sushi', 'Japanese', 12.00, 'HIGH', 5, 4, 0.8)
    ]

    actual_leaderboard = get_leaderboard(sort_by="wins")
    expected_leaderboard = [
        {
            'id': 1,
            'meal': 'Pizza',
            'cuisine': 'Italian',
            'price': 10.0,
            'difficulty': 'MED',
            'battles': 10,
            'wins': 6,
            'win_pct': 60.0
        },
        {
            'id': 2,
            'meal': 'Sushi',
            'cuisine': 'Japanese',
            'price': 12.0,
            'difficulty': 'HIGH',
            'battles': 5,
            'wins': 4,
            'win_pct': 80.0
        }
        ]
    assert actual_leaderboard == expected_leaderboard, f"Expected {expected_leaderboard}, got {actual_leaderboard}"

    expected_query = normalize_whitespace("""SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct 
    FROM meals WHERE deleted = false AND battles > 0
    ORDER BY wins DESC
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert expected_query == actual_query, f"The query did not match the expected structure."

def test_get_leaderboard_sort_by_win_pct(mock_cursor):
    """Test the leaderboard for sorting by win_pct."""
    mock_cursor.fetchall.return_value = [  
        (2, 'Sushi', 'Japanese', 12.00, 'HIGH', 5, 4, 0.8),
        (1, 'Pizza', 'Italian', 10.00, 'MED', 10, 6, 0.6)
    ]
    expected_leaderboard = [
        {
            'id': 2,
            'meal': 'Sushi',
            'cuisine': 'Japanese',
            'price': 12.0,
            'difficulty': 'HIGH', 
            'battles': 5,
            'wins': 4,
            'win_pct': 80.0
        },
        {
            'id': 1,
            'meal': 'Pizza',
            'cuisine': 'Italian',
            'price': 10.0,
            'difficulty': 'MED', 
            'battles': 10,
            'wins': 6,
            'win_pct': 60.0
        }
    ]
    actual_leaderboard = get_leaderboard(sort_by="win_pct")
    assert actual_leaderboard == expected_leaderboard, f"Expected {expected_leaderboard}, got {actual_leaderboard}"
    
    expected_query = normalize_whitespace("""SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct 
    FROM meals WHERE deleted = false AND battles > 0
    ORDER BY win_pct DESC
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert expected_query == actual_query, f"The query did not match the expected structure."

def test_get_leaderboard_invalid_sort_by():
    """Test error raising for an invalid sort paramenter."""
    with pytest.raises (ValueError, match = "Invalid sort_by parameter: invalid_sort"):
        get_leaderboard(sort_by = "invalid_sort")



def test_get_meal_by_id_found(mock_cursor):
    """Test to retrieve a meal by an ID where ID exists."""
    mock_cursor.fetchone.return_value = (1, 'Pizza', 'Italian', 10.0, 'MED', False)
    
    meal = get_meal_by_id(1)
    expected_meal = (1, 'Pizza', 'Italian', 10.0, 'MED')
    
    assert meal == expected_meal, f"Expected {expected_meal}, got {meal}"

    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, f"The query did not match the expected structure."


    expected_arguments = (1,)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    assert actual_arguments == expected_arguments, f"The query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_bad_id(mock_cursor):
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_id_deleted_meal(mock_cursor):
    mock_cursor.fetchone.return_value = (1, 'Pizza', 'Italian', 10.0, 'MED', True)

    with pytest.raises(ValueError, match = "Meal with ID 1 has been deleted"):
        get_meal_by_id(1)



def test_get_meal_by_name_found(mock_cursor):
    """Test to retrieve a meal by a name where the meal exists."""
    mock_cursor.fetchone.return_value = (1, 'Pizza', 'Italian', 10.0, 'MED', False)
    
    actual_meal = get_meal_by_name('Pizza')
    expected_meal = (1, 'Pizza', 'Italian', 10.0, 'MED')
    
    assert actual_meal == expected_meal, f"Expected {expected_meal}, got {actual_meal}"

    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, f"The query did not match the expected structure."


    expected_arguments = ('Pizza',)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    assert actual_arguments == expected_arguments, f"The query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_no_name(mock_cursor):
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match = "Meal with name Sushi not found"):
        get_meal_by_name('Sushi')

def test_get_meal_by_name_deleted_meal(mock_cursor):
    mock_cursor.fetchone.return_value = (1, 'Pizza', 'Italian', 10.0, 'MED', True)

    with pytest.raises(ValueError, match = "Meal with name Pizza has been deleted"):
        get_meal_by_name('Pizza')

"""
update meal stats (update_play_count / deleted_song)
    meal doesnt exist
    meal has been deleted
    desired result invalid
    
    has it been updated correctly
"""

def test_update_meal_stats_valid (mock_cursor):
    mock_cursor.fetchone.return_value = [False]

    update_meal_stats (meal_id = 1, results = "win")

    expected_query = normalize_whitespace("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_query == expected_query, f"The SQL query did not match the expected structure."

    actual_arguments = 


def test_update_meal_stats_not_found (mock_cursor):
    mock_cursor.fetchone.return_value = 

def test_update_meal_stats_deleted_meal (mock_cursor):
    mock_cursor.fetchone.return_value = 

def test_update_meal_stats_invalid_result (mock_cursor):
    mock_cursor.fetchone.return_value = 