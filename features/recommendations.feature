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
    Then I should see "Recommendations Demo RESTful Service" in the title
    And I should not see "404 Not Found"

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
