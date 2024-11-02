import pytest

from meal_max.models.kitchen_model import Meal
from meal_max.models.battle_model import BattleModel 

@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture #not 100% but they did something similar in playlist test
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stat function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")

"""Fixtures providing sample combatants (meals) for the tests."""
@pytest.fixture
def sample_combatant1():
    return Meal(1, 'Artist 1', 'Song 1', 2022, 'Pop', 180) ##

@pytest.fixture
def sample_combatant2():
    return Meal(2, 'Artist 2', 'Song 2', 2021, 'Rock', 155) ##

@pytest.fixture
def sample_battle(sample_combatant1, sample_combatant2):
    return [sample_combatant1, sample_combatant2]

def test_battle(battle_model, sample_battle, mock_update_meal_stats):
    """Running a test battle w/ mock function to test the update meal stats function"""
    battle_model.battle.extend(sample_battle)

    battle_model.battle()

    #not complete!!
    #kinda similar to the test_play_current_song function on the playlist tests

def test_battle_no_combatants(battle_model):
    """Test battle raises error when combatants list is empty."""
    battle_model.clear_combatants() #should we also check for when theres 1 combatant??

    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

def test_battle_one_combatant(battle_model, sample_combatant1):
    """Test battle raises error when combatants list has only 1 combatant"""
    battle_model.battle.extend(sample_combatant1) #not sure about this one

    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

def test_clear_combatants(battle_model, sample_battle):
    """Test clearing the entrire combatants list"""
    battle_model.battle.extend(sample_battle)

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after clearing"

#last 3 functions from battle_model remaining; have to fix up first battle() test

#Sophia do last three