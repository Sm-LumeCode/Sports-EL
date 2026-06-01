def test_create_player(client):
    response = client.post(
        "/players/",
        json={
            "name": "Lionel Messi",
            "age": 36,
            "sport": "Football",
            "position": "Forward",
            "team": "Inter Miami"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Lionel Messi"
    assert "id" in data

def test_get_players(client):
    response = client.get("/players/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Lionel Messi"
