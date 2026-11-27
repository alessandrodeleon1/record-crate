Feature: Creating releases and adding copies

  Scenario: A logged-in user creates a release
    Given I am logged in as "alice"
    When I create a release titled "Head Hunters" by "Herbie Hancock"
    Then I should be redirected to the detail page for "Head Hunters"

  Scenario: A logged-in user adds a copy they own
    Given a release "Kind of Blue" by "Miles Davis"
    And I am logged in as "alice"
    When I add a copy of "Kind of Blue" in "Vinyl" format
    Then I should own a copy of "Kind of Blue" in "Vinyl" format

  Scenario: Anonymous visitors cannot add copies
    Given a release "Kind of Blue" by "Miles Davis"
    When I add a copy of "Kind of Blue" in "Vinyl" format
    Then no copies of "Kind of Blue" should exist
