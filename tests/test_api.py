def test_endpoint_exist(client):
    reponse = client.post("/transcribe")
    assert reponse.status_code in [400,422]