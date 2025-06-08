Feature: Multi-agent research workflow

  Scenario: Successful research and writing workflow
    Given I have a research task "AI trends 2024"
    When I run the research workflow
    Then the researcher agent should gather information
    And the writer agent should create a report
    And the final output should contain key findings

  Scenario: Workflow with invalid task
    Given I have an invalid research task ""
    When I run the research workflow  
    Then I should receive an error message
    And no agents should be executed
