Feature: Browsing the catalogue

  Scenario: Home page lists recently added releases
    Given a release "Kind of Blue" by "Miles Davis"
    When I visit the home page
    Then I should see "Kind of Blue"
    And I should see "Miles Davis"

  Scenario: Artist page lists only that artist's releases
    Given a release "Kind of Blue" by "Miles Davis"
    And a release "Bitches Brew" by "Miles Davis"
    And a release "Blue Train" by "John Coltrane"
    When I visit the artist page for "Miles Davis"
    Then I should see "Kind of Blue"
    And I should see "Bitches Brew"
    And I should not see "Blue Train"

  Scenario: Searching releases by artist name
    Given a release "Kind of Blue" by "Miles Davis"
    And a release "Blue Train" by "John Coltrane"
    When I search the releases for "Coltrane"
    Then I should see the status code 200
    And I should see "Blue Train"
    And I should not see "Kind of Blue"

  Scenario: Random button opens a release
    Given a release "Kind of Blue" by "Miles Davis"
    When I click the random button
    Then I should be redirected to the detail page for "Kind of Blue"

  Scenario: Random button with an empty catalogue goes to listings
    Given the catalogue is empty
    When I click the random button
    Then I should be redirected to the listings page

  Scenario: Item page shows who owns the copy
    Given a release "Kind of Blue" by "Miles Davis"
    And a copy of "Kind of Blue" in "Vinyl" format owned by "alice"
    When I visit the item page for "Kind of Blue"
    Then I should see "alice"

  Scenario: Collection page shows a user's copies
    Given a release "Kind of Blue" by "Miles Davis"
    And a copy of "Kind of Blue" in "Vinyl" format owned by "alice"
    When I visit the collection of "alice"
    Then I should see "Kind of Blue"
