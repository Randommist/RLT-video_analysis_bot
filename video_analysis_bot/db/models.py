from tortoise import fields, Model


class Video(Model):
    id = fields.UUIDField(pk=True)
    creator_id = fields.CharField(max_length=255)
    video_created_at = fields.DatetimeField()
    views_count = fields.IntField()
    likes_count = fields.IntField()
    comments_count = fields.IntField()
    reports_count = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta(Model.Meta):
        table = "videos"


class VideoSnapshot(Model):
    id = fields.UUIDField(pk=True)
    video = fields.ForeignKeyField("models.Video", related_name="snapshots")
    views_count = fields.IntField()
    likes_count = fields.IntField()
    comments_count = fields.IntField()
    reports_count = fields.IntField()
    delta_views_count = fields.IntField()
    delta_likes_count = fields.IntField()
    delta_comments_count = fields.IntField()
    delta_reports_count = fields.IntField()
    created_at = fields.DatetimeField()
    updated_at = fields.DatetimeField()

    class Meta(Model.Meta):
        table = "video_snapshots"
