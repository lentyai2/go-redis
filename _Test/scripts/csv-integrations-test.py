import csv

class Record:
    def __init__(self, email, integration_type, active, agent_id, application, assignee, attachements, cert_info, cert_info_date, company, created_ts, industry, isv_date, lead_source, meeting_type, mid, private_description, product, products_discussed, relationship_manager, reporter, sales_agent, sales_group, sandbox_config, stakeholder_contact, stakeholder_developer,	status, step, summary, team_assigned, terminal_info, terminal_info_date, third_party_agent, ticket,updated_ts):
        self.email = email
        self.integration_type = integration_type
        self.active = active
        self.agent_id = agent_id
        self.application = application
        self.assignee = assignee
        self.attachements = attachements
        self.cert_info = cert_info
        self.cert_info_date = cert_info_date
        self.company = company
        self.created_ts = created_ts
        self.industry = industry
        self.isv_date = isv_date
        self.lead_source = lead_source
        self.meeting_type = meeting_type
        self.mid = mid
        self.salary = salary
        self.name = name
        self.department = department
        self.salary = salary
        self.name = name
        self.department = department
        self.salary = salary
        self.name = name
        self.department = department
        self.salary = salary
        self.name = name
        self.department = department
        self.salary = salary
        self.name = name
        self.department = department
        self.salary = salary
        self.name = name
        self.department = department
        self.salary = salary
        self.name = name
        self.department = department
        self.salary = salary
        self.name = name
        self.department = department
        self.salary = salary                                                                                                        

    def __repr__(self):
        return f"Record({self.name}, {self.department}, {self.salary})"

records = []

with open('dynamo-integrations.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header row
    for row in reader:
        name, department, salary = row
        record = Record(name, department, int(salary))
        records.append(record)

print(records)