import requests
import os
from datetime import datetime, timedelta
from dateutil import parser
import pytz
from terminaltables import AsciiTable
from dotenv import load_dotenv

TOWN_ID = 4
CATALOGUE_ID = 48
DEFAULT_PERIOD = 0
VACANCIES_COUNT = 100


def get_vacancies_hh(text, area, last_month_date):
    vacancies = []
    total_vacancies = 0
    page = 0
    per_page = 100

    while True:
        params = {
            'text': text,
            'area': area,
            'per_page': per_page,
            'page': page,
            'date_from': last_month_date
        }
        response = requests.get('https://api.hh.ru/vacancies', params=params)

        if response.status_code != 200:
            print(f"Ошибка: {response.status_code} - {response.text}")
            break

        data = response.json()

        total_vacancies = data.get('found', 0)

        if not data['items']:
            break

        vacancies.extend(data['items'])

        if page * per_page >= 2000 or len(data['items']) < per_page:
            break

        page += 1

    return vacancies, total_vacancies


def predict_rub_salary_hh(vacancy):
    salary = vacancy.get('salary')
    if not salary:
        return None

    if salary.get('currency') != 'RUR':
        return None

    salary_from = salary.get('from')
    salary_to = salary.get('to')

    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    if salary_from:
        return salary_from * 1.2
    if salary_to:
        return salary_to * 0.8

    return None


def collect_hh_statistics(languages, area):
    last_month_date = (datetime.now(pytz.timezone('Europe/Moscow')) - timedelta(days=30)).isoformat()
    language_stats = {}

    for language in languages:
        all_vacancies, total_vacancies = get_vacancies_hh(f'программист {language}', area, last_month_date)

        predicted_salaries = [
            salary for vacancy in all_vacancies if (salary := predict_rub_salary_hh(vacancy))
        ]

        language_stats[language] = {
            'vacancies_found': total_vacancies,
            'vacancies_processed': len(predicted_salaries),
            'average_salary': int(sum(predicted_salaries) / len(predicted_salaries)) if predicted_salaries else None
        }

    return language_stats


def predict_rub_salary_sj(vacancy):
    salary_from = vacancy.get('payment_from')
    salary_to = vacancy.get('payment_to')

    if salary_from and salary_to:
        return (salary_from + salary_to) / 2

    if salary_from:
        return salary_from
    if salary_to:
        return salary_to

    return None


def get_vacancies_sj(sj_secret_key, language, page_number):
    sj_params = {
        'town': TOWN_ID,
        'catalogues': CATALOGUE_ID,
        'period': DEFAULT_PERIOD,
        'count': VACANCIES_COUNT,
        'page': page_number,
        'keyword': language,
        'no_agreement': 1
    }
    headers = {'X-Api-App-Id': sj_secret_key}
    response = requests.get('https://api.superjob.ru/2.0/vacancies/', headers=headers, params=sj_params)
    response.raise_for_status()
    return response.json()


def collect_sj_statistics(languages, sj_secret_key):
    stats = {}
    for language in languages:
        all_vacancies = []
        processed_vacancies = 0
        total_salary = 0

        try:
            page_number = 0
            while True:
                jobs = get_vacancies_sj(sj_secret_key, language, page_number)
                vacancies = jobs.get('objects', [])
                total_vacancies = jobs.get('total', 0)

                if not vacancies:
                    break

                all_vacancies.extend(vacancies)

                if len(vacancies) < VACANCIES_COUNT:
                    break

                page_number += 1

            for vacancy in all_vacancies:
                salary = predict_rub_salary_sj(vacancy)
                if salary:
                    total_salary += salary
                    processed_vacancies += 1
                else:
                    print(f"Вакансия без зарплаты: {vacancy['profession']}")

            stats[language] = {
                "vacancies_found": len(all_vacancies),
                "vacancies_processed": processed_vacancies,
                "average_salary": int(total_salary / processed_vacancies) if processed_vacancies > 0 else None
            }

        except requests.exceptions.HTTPError as err:
            print(f'Не удалось сделать на sj запрос для языка {language}\n {err}')

    return stats


def print_statistics(title, stats):
    table_data = [['Язык программирования', 'Найдено вакансий', 'Обработано вакансий', 'Средняя зарплата']]
    for language, data in stats.items():
        table_data.append([
            language,
            data['vacancies_found'],
            data['vacancies_processed'],
            data['average_salary'] if data['average_salary'] is not None else 'Не указана'
        ])

    table = AsciiTable(table_data)
    print(f"\n+{title}+\n{table.table}\n")


def main():
    load_dotenv()
    sj_secret_key = os.getenv('SJ_SECRET_KEY')
    languages = ['python', 'c', 'c#', 'c++', 'java', 'js', 'ruby', 'go', '1с']

    hh_stats = collect_hh_statistics(languages, '1')
    print_statistics("HeadHunter Moscow", hh_stats)

    sj_stats = collect_sj_statistics(languages, sj_secret_key)
    print_statistics("SuperJob Moscow", sj_stats)


if __name__ == "__main__":
    main()

