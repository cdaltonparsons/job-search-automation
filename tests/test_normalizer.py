from normalizer import Job

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