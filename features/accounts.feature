Feature: Accounts

  Scenario: Registering a new account
    When I register with username "bob" and password "S3cure-pass-123"
    Then I should be redirected to the login page
    And a user named "bob" should exist

  Scenario: Logging in with valid credentials
    Given a user named "carol"
    When I log in with username "carol" and password "test-pass-123"
    Then I should be redirected to the home page
    And I should be logged in

  Scenario: Logging in with a wrong password fails
    Given a user named "carol"
    When I log in with username "carol" and password "wrong-password"
    Then I should see the status code 200
    And I should not be logged in

  Scenario: Logging out
    Given I am logged in as "carol"
    When I log out
    Then I should be redirected to the home page
    And I should not be logged in

  Scenario: Anonymous visitors see login and register links
    When I visit the home page
    Then I should see "Login"
    And I should see "Register"
