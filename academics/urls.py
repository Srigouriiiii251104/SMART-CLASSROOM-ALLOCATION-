from django.urls import path

from .api import (
    FreeClassroomAPIView,
    TimetableEntryListAPIView,
    TimetableGenerateAPIView,
    TimetableMoveAPIView,
)
from .views import (
    ClassroomCreateView,
    ClassroomDeleteView,
    ClassroomListView,
    ClassroomUpdateView,
    GenerateTimetableView,
    TimetableBoardView,
)


app_name = "academics"

urlpatterns = [
    path("classrooms/", ClassroomListView.as_view(), name="classroom_list"),
    path("classrooms/add/", ClassroomCreateView.as_view(), name="classroom_add"),
    path("classrooms/<int:pk>/edit/", ClassroomUpdateView.as_view(), name="classroom_edit"),
    path("classrooms/<int:pk>/delete/", ClassroomDeleteView.as_view(), name="classroom_delete"),
    path("timetable/", TimetableBoardView.as_view(), name="timetable_board"),
    path("timetable/generate/", GenerateTimetableView.as_view(), name="timetable_generate"),
    path("api/timetable/", TimetableEntryListAPIView.as_view(), name="api_timetable_list"),
    path("api/timetable/generate/", TimetableGenerateAPIView.as_view(), name="api_timetable_generate"),
    path("api/timetable/move/", TimetableMoveAPIView.as_view(), name="api_timetable_move"),
    path("api/classrooms/free/", FreeClassroomAPIView.as_view(), name="api_free_classrooms"),
]
