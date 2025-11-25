Feature: The recommendation service back-end
    As a Recommendation Service developer
    I need a RESTful catalog service
    So that I can keep track of all recommendation

Background:
    Given the following recommendations
        | id | name                   | base_product_id | recommended_product_id | recommendation_type | status   | likes |
        | 1  | Phone X -> Case Y      | 101             | 201                    | accessory           | draft    | 0     |
        | 23 | Clothes X -> Clothes Y | 345             | 873                    | up_sell             | active   | 23    |
        | 109| Jeans X -> Belt Y      | 723             | 908                    | cross_sell          | draft    | 0     |
        | 85 | Bag X -> Bag Y         | 196             | 292                    | trending            | inactive | 45    |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendations Demo REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Recommendation
    When I visit the "Home Page"
    And I set the "name" to "Candle X -> Candle Y"
    And I set the "base_product_id" to "801"
    And I set the "recommended_product_id" to "901"
    And I select "up_sell" in the "recommendation_type" dropdown
    And I select "draft" in the "status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Clear" button
    Then the "id" field should be empty
    And the "name" field should be empty
    And the "base_product_id" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "801" in the "base_product_id" field
    And I should see "901" in the "recommended_product_id" field
    And I should see "up_sell" in the "recommendation_type" dropdown
    And I should see "draft" in the "status" dropdown
    And I should see "0" in the "likes" field

Scenario: Search for accessory
    When I visit the "Home Page"
    And I select "accessory" in the "recommendation_type" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Phone X -> Case Y" in the results

Scenario: List all recommendations
    When I visit the "Home Page"
    And I press the "List" button
    Then I should see the message "Success"
    And I should see "Phone X -> Case Y" in the results
    And I should see "Clothes X -> Clothes Y" in the results
    And I should see "Jeans X -> Belt Y" in the results
    And I should see "Bag X -> Bag Y" in the results

Scenario: Like a recommendation
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "base_product_id" to "345"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "345" in the "base_product_id" field
    And I should see "873" in the "recommended_product_id" field
    And I should see "up_sell" in the "recommendation_type" dropdown
    And I should see "active" in the "status" dropdown
    And I should see "23" in the "likes" field
    When I press the "Like" button
    Then I should see "24" in the "likes" field


Scenario: Dislike a recommendation
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "base_product_id" to "345"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "345" in the "base_product_id" field
    And I should see "873" in the "recommended_product_id" field
    And I should see "up_sell" in the "recommendation_type" dropdown
    And I should see "active" in the "status" dropdown
    And I should see "23" in the "likes" field
    When I press the "Dislike" button
    Then I should see "22" in the "likes" field

Scenario: Search for draft recommendations
    When I visit the "Home Page"
    And I press the "Clear" button
    And I select "draft" in the "status" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Jeans X -> Belt Y" in the results
    And I should see "Phone X -> Case Y" in the results
    And I should not see "Clothes X -> Clothes" in the results

Scenario: Update a Recommendation
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "base_product_id" to "723"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Jeans X -> Belt Y" in the "name" field
    And I should see "723" in the "base_product_id" field
    And I should see "908" in the "recommended_product_id" field
    And I should see "cross_sell" in the "recommendation_type" dropdown
    When I change "name" to "Jeans X -> Premium Belt Y"
    And I press the "Update" button
    Then I should see the message "Updated successfully."
    When I copy the "base_product_id" field
    And I press the "Clear" button
    And I paste the "base_product_id" field
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Jeans X -> Premium Belt Y" in the "name" field
    When I press the "Clear" button
    And I press the "List" button
    Then I should see the message "Success"
    And I should see "Jeans X -> Premium Belt Y" in the results
    And I should not see "Jeans X -> Belt Y" in the results

Scenario: Delete a recommendation
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "base_product_id" to "101"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Phone X -> Case Y" in the "name" field
    And I should see "accessory" in the "recommendation_type" dropdown
    And I should see "draft" in the "status" dropdown
    When I press the "Delete" button
    Then I should see the message "Recommendation deleted."
    When I press the "Clear" button
    And I set the "id" to "1"
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found"

Scenario: Activate a Recommendation
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "base_product_id" to "196"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Bag X -> Bag Y" in the "name" field
    And I should see "196" in the "base_product_id" field
    And I should see "292" in the "recommended_product_id" field
    And I should see "trending" in the "recommendation_type" dropdown
    And I should see "inactive" in the "status" dropdown
    When I select "active" in the "status" dropdown
    And I press the "Update" button
    Then I should see the message "Updated successfully."
    When I copy the "base_product_id" field
    And I press the "Clear" button
    And I paste the "base_product_id" field
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "active" in the "status" field

Scenario: Deactivate a Recommendation
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "base_product_id" to "345"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Clothes X -> Clothes Y" in the "name" field
    And I should see "345" in the "base_product_id" field
    And I should see "873" in the "recommended_product_id" field
    And I should see "up_sell" in the "recommendation_type" dropdown
    And I should see "active" in the "status" dropdown
    When I select "inactive" in the "status" dropdown
    And I press the "Update" button
    Then I should see the message "Updated successfully."
    When I copy the "base_product_id" field
    And I press the "Clear" button
    And I paste the "base_product_id" field
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "active" in the "status" field