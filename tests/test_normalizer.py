from normalizer import Job, normalize

def test_job_defaults():
    job = Job(
        id= "123",
        title= "Test title",
        company= "Best company",
        location= "Close to home",
        url= "bestjob.com",
        source= "linkedIn",
        posted_date= "Today",
        description= "test description"
    )
    assert job.remote == False
    assert job.seen == False
    assert job.applied == False
    assert job.notes == None
    assert job.salary == None

def test_job_fields():
    job = Job(
        id= "123",
        title= "Test title",
        company= "Best company",
        location= "Close to home",
        url= "bestjob.com",
        source= "linkedIn",
        posted_date= "Today",
        description= "test description",
        remote= True,
        applied= False,
        notes= "Test notes",
        salary= "150000"
    )
    assert job.id == "123"
    assert job.url == "bestjob.com"
    assert job.salary == "150000"

def test_normalize_maps_fields():
    raw = {
        "title": "Software Engineer",
        "company": "Acme Corp",
        "url": "https://acme.com/jobs/1",
        "location": "Remote",
        "source": "rss",
        "posted_date": "2026-06-01",
        "description": "Build cool things.",
        "remote": True,
        "salary": "120000",
        "notes": None,
    }
    job = normalize(raw)
    assert job.title == "Software Engineer"
    assert job.remote == True
    assert job.notes == None
    assert job.description == "Build cool things."

def test_normalize_deterministic():
    raw = {
        "title": "Software Engineer",
        "company": "Acme Corp",
        "url": "https://acme.com/jobs/1",
        "location": "Remote",
        "source": "rss",
        "posted_date": "2026-06-01",
        "description": "Build cool things.",
        "remote": True,
        "salary": "120000",
        "notes": None,
    }
    job1 = normalize(raw)
    job2 = normalize(raw)

    assert job1.id == job2.id

def test_normalize_sparse_dict():
    raw = {
        "title": "Software Engineer",
        "company": "Acme Corp",
        "url": "https://acme.com/jobs/1",
    }
    job = normalize(raw)
    assert job.salary is None
    assert job.remote == False
