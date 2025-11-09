Feature: List Recommendations
    As an eCommerce administrator
    I need to list product recommendations
    So that I can view all recommendation relationships

Background:
    Given the recommendations service is running
    And I am on the home page

@list
Scenario: List all recommendations
    When I click the "List" button
    Then I should see a table with recommendation data
    And the table should have columns: ID, Name, Base Product ID, Recommended Product ID, Type, Status, Likes

@list
Scenario: List shows correct data for each recommendation
    When I click the "List" button
    Then I should see a table with recommendation data
    And each recommendation should display correct data
