Feature: Listing and buying copies

  Scenario: Only copies marked for sale appear in listings
    Given a release "Kind of Blue" by "Miles Davis"
    And a release "Blue Train" by "John Coltrane"
    And a copy of "Kind of Blue" in "Vinyl" format listed for sale at 25.00 owned by "alice"
    And a copy of "Blue Train" in "Vinyl" format owned by "alice"
    When I visit the listings page
    Then I should see "Kind of Blue"
    And I should not see "Blue Train"

  Scenario: A logged-in buyer adds a listed copy to their cart
    Given a release "Kind of Blue" by "Miles Davis"
    And a copy of "Kind of Blue" in "Vinyl" format listed for sale at 25.00 owned by "alice"
    And I am logged in as "bob"
    When I add "Kind of Blue" to my cart
    Then I should be redirected to the listings page
    And I should have a cart containing "Kind of Blue"

  Scenario: Anonymous visitors cannot add to cart
    Given a release "Kind of Blue" by "Miles Davis"
    And a copy of "Kind of Blue" in "Vinyl" format listed for sale at 25.00 owned by "alice"
    When I add "Kind of Blue" to my cart
    Then I should be redirected to the login page
    And no cart should exist

  Scenario: Owners cannot buy their own copy
    Given a release "Kind of Blue" by "Miles Davis"
    And a copy of "Kind of Blue" in "Vinyl" format listed for sale at 25.00 owned by "alice"
    And I am logged in as "alice"
    When I add "Kind of Blue" to my cart
    Then I should see the message "You can't buy your own item."
    And no cart should exist

  Scenario: Adding to cart requires a POST request
    Given a release "Kind of Blue" by "Miles Davis"
    And a copy of "Kind of Blue" in "Vinyl" format listed for sale at 25.00 owned by "alice"
    And I am logged in as "bob"
    When I try to add "Kind of Blue" to my cart with a GET request
    Then I should see the status code 405

  Scenario: An owner can take a listing down
    Given a release "Kind of Blue" by "Miles Davis"
    And a copy of "Kind of Blue" in "Vinyl" format listed for sale at 25.00 owned by "alice"
    And I am logged in as "alice"
    When I unlist "Kind of Blue"
    Then the copy of "Kind of Blue" should not be for sale

  Scenario: An owner can list a copy for sale
    Given a release "Kind of Blue" by "Miles Davis"
    And a copy of "Kind of Blue" in "Vinyl" format owned by "alice"
    And I am logged in as "alice"
    When I list "Kind of Blue" for sale at 30.00
    Then the copy of "Kind of Blue" should be for sale
    And the copy of "Kind of Blue" should be priced at 30.00

  Scenario: Non-owners cannot list someone else's copy
    Given a release "Kind of Blue" by "Miles Davis"
    And a copy of "Kind of Blue" in "Vinyl" format owned by "alice"
    And I am logged in as "bob"
    When I list "Kind of Blue" for sale at 30.00
    Then I should see the status code 404
    And the copy of "Kind of Blue" should not be for sale
