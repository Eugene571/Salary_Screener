# Salary Screener

This project collects and analyzes job vacancies data from two popular job search platforms: HeadHunter and SuperJob. It retrieves information about programming job vacancies in Moscow, including the number of vacancies found, processed vacancies, and average salaries for different programming languages.

## Features

- Fetch job vacancies from HeadHunter and SuperJob APIs.
- Analyze job vacancies based on programming languages.
- Calculate average salaries for each language.
- Display the results in a well-formatted ASCII table.

## Requirements

This project requires Python 3.x and the following packages:

- `requests`
- `python-dateutil`
- `pytz`
- `terminaltables`
- `python-dotenv`

You can install the required packages using the following command:

```bash
pip install -r requirements.txt
```

## Setup
1. Clone this repository:
```bash
git clone https://github.com/Eugene571/Salary_Screener
cd Salary_Screener
```

2. Create a .env file in the root directory of the project and add your SuperJob API key:
```makefile
SJ_SECRET_KEY=<your_superjob_api_key>
```

## Usage
Run the main script to fetch and display job statistics:
```bash
python salary_screener.py
```

The output will show the number of job vacancies found, processed vacancies, and average salaries for specified programming languages from both platforms.

## Supported Programming Languages
The project currently supports the following programming languages for vacancy analysis:

- Python
- C
- C#
- C++
- Java
- JavaScript (JS)
- Ruby
- Go
- 1C

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

### This project is done for educational purposes as a part of the dvmn.org course