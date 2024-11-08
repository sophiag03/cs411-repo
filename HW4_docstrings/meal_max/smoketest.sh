#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}




clear_catalog() {
  echo "Clearing the meals..."
  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
}

delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID:($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

#create-meal
create_meal(){
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal ($meal, $cuisine, $price, $difficulty) to the meals..."
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Song added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}

#get-meal-by-id
get_meal_by_id(){
  meal_id=$1

  echo "Retrieving meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

#get-meal-by-name
get_meal_by_name(){
  meal_name=$1

  echo "Getting meal by meal name (Meal name: '$meal_name')..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by meal name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (by meal name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by meal name."
    exit 1
  fi
}

#battle


#clear-combatants
clear_combatants() {
  echo "Clearing all combatants from battle..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants") #fixed this to get this test to pass
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}


#get-combatants
get_combatants() {
  echo "Retrieving all combatants from battle..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "All combatants retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Combatants JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve all combatants from battle."
    exit 1
  fi
}

#prep-combatant
# prep_combatant(){
#   meal=$1
#   cuisine=$2
#   price=$3
#   difficulty=$4

#   echo "Preparing a combatant: ($meal, $cuisine, $price, $difficulty)..."
#   response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
#     -H "Content-Type: application/json" \
#     -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":"$difficulty"}")

# # response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" \
# #     -d "{\"Meal\":\"$Meal\"}")

#   if echo "$response" | grep -q '"status": "success"'; then
#     echo "Prepared combatant successfully."
#     if [ "$ECHO_JSON" = true ]; then
#       echo "Combatants JSON:"
#       echo "$response" | jq .
#     fi
#   else 
#     echo "Failed to prepare combatant."
#     exit 1
#   fi
# }

prep_combatant(){
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Preparing a combatant: ($meal, $cuisine, $price, $difficulty)..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Prepared combatant successfully: Pizza"
    if [ "$ECHO_JSON" = true ]; then
      echo "Combatants JSON:"
      echo "$response" | jq .
    fi
  else 
    echo "Failed to prepare combatant. Response was:"
    echo "$response"
    exit 1
  fi
}



#leaderboard
leaderboard(){
  echo "Getting all meals sorted by sort_by..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON:"
      echo "$response" | jq .
    fi
  else 
    echo "Failed to get leaderboard."
    exit 1
  fi
}




#call smoketests

check_health
check_db

clear_catalog

create_meal "Pizza" "Italian" 10.99 "MED"
create_meal "Sushi" "Japanese" 12.00 "HIGH"

get_meal_by_id 2
get_meal_by_name "Pizza"

delete_meal_by_id 2

clear_combatants
prep_combatant "Pizza" "Italian" 10.99 "MED"
get_combatants
leaderboard
