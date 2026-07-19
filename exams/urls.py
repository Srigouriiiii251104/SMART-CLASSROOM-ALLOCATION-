from django.urls import path

from .views import (
    AllocateExamView,
    ExamAllocationAPIView,
    ExamScheduleCreateView,
    ExamScheduleDetailView,
    ExamScheduleListView,
)


app_name = "exams"

urlpatterns = [
    path("", ExamScheduleListView.as_view(), name="exam_list"),
    path("add/", ExamScheduleCreateView.as_view(), name="exam_add"),
    path("<int:pk>/", ExamScheduleDetailView.as_view(), name="exam_detail"),
    path("<int:pk>/allocate/", AllocateExamView.as_view(), name="allocate"),
    path("api/<int:pk>/allocate/", ExamAllocationAPIView.as_view(), name="api_allocate"),
]
