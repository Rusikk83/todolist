
# Register your models here.
from django.contrib import admin

from goals.models import GoalCategory, GoalComment, Goal


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created", "updated")
    readonly_fields = ('created', 'updated')
    search_fields = ["title"]
    list_filter = ['is_deleted']


class CommentsInLine(admin.StackedInline):
    model = GoalComment
    extra = 0


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "created", "updated")
    readonly_fields = ('created', 'updated')
    search_fields = ("title", "description")
    list_filter = ('status', 'priority')
    inlines = [CommentsInLine]
