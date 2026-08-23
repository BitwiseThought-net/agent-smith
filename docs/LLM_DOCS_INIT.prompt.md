
Fully analyze the project.
If project is attached as a zip file. Assume it contains the latest project code, checked in to the git repo.
Write a docs/ folder to document the project with .md files.
Populate and organize the docs/ folder appropriately with stub .md files.

For stub .md files:
* In each file add a list of TODO documentation tasks, for a LLM to read, with BRIEF instructions on what code, file, feature, prerequisite, tool, etc. needs to be documented.
* Use the TODO list to indicate what needs to be documented, and provide enough context for the LLM to understand what is required.
* Do not use em dashes, instead use hypens, use asterisks or dashes for bullet points.

Then add a .md file at the root of docs/ with LLM prompt instructions, which instructs the LLM when given one of the TODO stub .md files, to populate it for human consumption, appropriately and fully (based on the TODO information within it), then remove the completed TODO item.

While populating, instruct it to:
* Organize documentation cleanly.
* At the beginning, make sure there's a summary describing the project.
* Include all the available config settings, their default values and their usage.
* Include any/all the --flags or options that can be passed in, and their differing functionality.
* Include any setup steps required for prerequisites.
* Include clear configuration steps.
* As needed, create any additional stub .md files and populate their documentation tasks, (as described in the "For stub .md files" above).
* Do not use em dashes, instead use hypens, use asterisks or dashes for bullet points.