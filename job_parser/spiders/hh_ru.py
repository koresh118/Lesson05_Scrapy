import scrapy
from scrapy.http import HtmlResponse
from job_parser.items import JobParserItem


class HhRuSpider(scrapy.Spider):
    name = 'hh_ru'
    allowed_domains = ['hh.ru']
    start_urls = [
        'https://omsk.hh.ru/search/vacancy?area=68&area=1308&part_time=temporary_job_true&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&text=Администратор&ored_clusters=true'
#        'https://omsk.hh.ru/search/vacancy?text=&area=68'
    ]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").get()
        if next_page:
            yield response.follow(next_page, self.parse)

        vacancies_links = response.xpath("//a[@data-qa = 'serp-item__title']/@href").getall()
        for link in vacancies_links:
            yield response.follow(link, callback=self.parse_vacansy)

        print('\n######################\n%s\n######################\n'%response.url)

    def parse_vacansy(self, response:HtmlResponse):
        vacansies_name = response.xpath("//h1[@data-qa='vacancy-title']//text()").get()
        vacancies_url = response.url
        vacancies_salary = response.xpath("//span[@data-qa='vacancy-salary-compensation-type-net']/text()").getall()
        salary = ""
        for i in range(len(vacancies_salary)):
            coint = vacancies_salary[i].replace("\xa0", "")
            vacancies_salary[i] = coint
#            salary += vacancies_salary[i]
#        vacancies_salary = salary

        if vacancies_salary:
            for i in range(len(vacancies_salary)):
                if (vacancies_salary[i] == "от "):
                    vacancy_min_salary = vacancies_salary[i + 1]
                    if (vacancies_salary[i + 2] != " до "):
                        vacancy_currency = vacancies_salary[i + 3]
                elif (vacancies_salary[i] == " до "):
                    vacancy_max_salary = vacancies_salary[i + 1]
                    vacancy_currency = vacancies_salary[i + 3]

        yield JobParserItem (
            name = vacansies_name,
            url = vacancies_url,
            min_salary = vacancy_min_salary,
            max_salary = vacancy_max_salary,
            currency = vacancy_currency
        )
