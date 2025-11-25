Feature: The recommendation service back-end
    As a Recommendation Service developer
    I need a RESTful catalog service
    So that I can keep track of all recommendation

Background:
Given the following recommendations
        | Recommendation Id    | Name                     |Base Product ID | Recommended Product ID | Recommendation Type  | Status   | Likes
        | 1                    | Phone X -> Case Y        |101             | 201                    | accessory            | draft    | 0
        | 23                   | Clothes X -> Clothes Y   |345             | 873                    | up_sell              | active   | 23
        | 109                  | Jeans X -> Belt Y        |723             | 908                    | cross_sell           | draft    | 0
        | 85                   | Bag X -> Bag Y           |196             | 292                    | trending             | inactive | 45

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendations Demo REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Recommendation
    When I visit the "Home Page"
    And I set the "Name" to "Candle X -> Candle Y"
    And I set the "Base Product ID" to "801"
    And I set the "Recommended Product ID" to "901"
    And I select "up_sell" in the "Recommendation Type" dropdown
    And I select "draft" in the "Status" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Recommendation Id" field
    And I press the "Clear" button
    Then the "Recommendation Id" field should be empty
    And the "Name" field should be empty
    And the "Base Product ID" field should be empty
    When I paste the "Recommendation Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see the "801" in the "Base Product ID" field
    And I should see the "901" in the "Recommended Product ID" field
    And I should see "up_sell" in the "Recommendation Type" dropdown
    And I should see "draft" in the "Status" dropdown
    And I should see "0" in the "Likes" field

Scenario: Like a recommendation
    When I set the "Recommendation Id" field to "23"
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see the "345" in the "Base Product ID" field
    And I should see the "873" in the "Recommended Product ID" field
    And I should see "up_sell" in the "Recommendation Type" dropdown
    And I should see "active" in the "Status" dropdown
    And I should see "23" in the "Likes" field
    When I press the "Like" button
    And I should see "24" in the "Likes" field

Scenario: Dislike a recommendation
    When I set the "Recommendation Id" field to "23"
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see the "345" in the "Base Product ID" field
    And I should see the "873" in the "Recommended Product ID" field
    And I should see "up_sell" in the "Recommendation Type" dropdown
    And I should see "active" in the "Status" dropdown
    And I should see "24" in the "Likes" field
    When I press the "Dislike" button
    And I should see "23" in the "Likes" field


Scenario: Search for accessory
    When I visit the "Home Page"
    And I set the "Recommendation Type" to "accessory"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Phone X -> Case Y" in the results

Scenario: Search for active
    When I visit the "Home Page"
    And I select "draft" in the "Status" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "1" in the results
    And I should see "109" in the results
    And I should not see "23" in the results

Scenario: List all recommendations
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "1" in the results
    And I should see "23" in the results
    And I should see "109" in the results
    And I should see "85" in the results
