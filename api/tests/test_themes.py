import uuid


async def test_health_returns_ok(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


async def test_create_theme_returns_201_with_generated_fields(client):
    res = await client.post("/themes", json={"title": "Next.jsの最新動向"})
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "Next.jsの最新動向"
    assert body["id"]  # 採番されている（UUID文字列）
    assert body["created_at"] is not None  # サーバー側で埋まっている


async def test_empty_title_is_rejected_with_422(client):
    """バリデーションはフロントではなくAPIの責務、の回帰テスト"""
    res = await client.post("/themes", json={"title": ""})
    assert res.status_code == 422


async def test_get_unknown_theme_returns_404(client):
    unknown = uuid.uuid4()
    assert (await client.get(f"/themes/{unknown}")).status_code == 404


async def test_patch_updates_only_given_field(client):
    created = (
        await client.post(
            "/themes", json={"title": "元のタイトル", "description": "元の説明"}
        )
    ).json()

    res = await client.patch(
        f"/themes/{created['id']}", json={"title": "新しいタイトル"}
    )

    assert res.status_code == 200
    assert res.json()["title"] == "新しいタイトル"
    assert res.json()["description"] == "元の説明"  # 消えていない


async def test_patch_updates_updated_at_but_not_created_at(client):
    created = (await client.post("/themes", json={"title": "元のタイトル"})).json()
    assert created["updated_at"] == created["created_at"]  # 作成直後は同じ

    updated = (
        await client.patch(f"/themes/{created['id']}", json={"title": "新しいタイトル"})
    ).json()

    assert updated["created_at"] == created["created_at"]  # 作成日時は動かない
    assert updated["updated_at"] != created["updated_at"]  # 更新日時は変わる


async def test_delete_then_get_returns_404(client):
    created = (await client.post("/themes", json={"title": "消す"})).json()
    assert (await client.delete(f"/themes/{created['id']}")).status_code == 204
    assert (await client.get(f"/themes/{created['id']}")).status_code == 404
