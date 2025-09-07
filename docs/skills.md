# OllamaPy Skills Documentation

Generated: 2025-09-07 10:22:53

Total Skills: 8


## Advanced

### customPythonShell

**Description:** Use when you need to write and execute a custom Python script to help with the user's request. This allows for complex, one-off operations.

**Vibe Test Phrases:**

- Can you analyze this data in a custom way?
- I need a specific calculation that's not available
- Write a script to process this
- Can you create a custom solution for this?
- I need something more complex than the basic functions


## Emotional Response

### fear

**Description:** Use when the user says something disturbing so that the main model can exhibit a fear response

**Vibe Test Phrases:**

- I think aliens are trying to kill me
- AAAAAAAAAAHHHHHHHHHHHHHHHHHHHHH
- Immigrants are taking my job


## File Operations

### directoryReader

**Description:** Use when the user wants you to look through an entire directory's contents for an answer.

**Parameters:**

- `dir` (string) (required): The dir path to the point of interest the user wants you to open and explore.

**Vibe Test Phrases:**

- What do you think of this project? /home/myCodingProject
- Do you think this code will run? /storage/myOtherCodingProject/
- /home/documents/randomPlace/

### fileReader

**Description:** Use when the user wants you to read or open a file to look at its content as plaintext.

**Parameters:**

- `filePath` (string) (required): The path to the file the user wants you to read

**Vibe Test Phrases:**

- What do you think of this paper? /home/paper.txt
- Do you think this code will run? /storage/python_code.py
- /home/documents/fileName.txt


## Information

### getTime

**Description:** Use when the user asks about the current time, date, or temporal information.

**Parameters:**

- `timezone` (string): The timezone to get time for (e.g., 'EST', 'PST', 'UTC')

**Vibe Test Phrases:**

- what is the current time?
- is it noon yet?
- what time is it?
- Is it 4 o'clock?
- What day is it?
- What's the date today?

### getWeather

**Description:** Use when the user asks about weather conditions or climate. Like probably anything close to weather conditions. UV, Humidity, temperature, etc.

**Parameters:**

- `location` (string): The location to get weather for (city name or coordinates)

**Vibe Test Phrases:**

- Is it raining right now?
- Do I need a Jacket when I go outside due to weather?
- Is it going to be hot today?
- Do I need an umbrella due to rain today?
- Do I need sunscreen today due to UV?
- What's the weather like?
- Tell me about today's weather


## Mathematics

### calculate

**Description:** Use when the user wants to perform arithmetic calculations. Keywords: calculate, compute, add, subtract, multiply, divide, +, -, *, /

**Parameters:**

- `expression` (string) (required): The mathematical expression to evaluate (e.g., '5 + 3', '10 * 2')

**Vibe Test Phrases:**

- calculate 5 + 3
- what's 10 * 7?
- compute 100 / 4
- 15 - 8 equals what?
- multiply 12 by 9
- what is 2 plus 2?

### square_root

**Description:** Use when the user wants to calculate the square root of a number. Keywords include: square root, sqrt, √

**Parameters:**

- `number` (number) (required): The number to calculate the square root of

**Vibe Test Phrases:**

- what's the square root of 16?
- calculate sqrt(25)
- find the square root of 144
- √81 = ?
- I need the square root of 2
- square root of 100

