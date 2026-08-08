from rest_framework.routers import DefaultRouter
from .views import FoodItemViewSet, DailyMenuViewSet

router = DefaultRouter()
router.register("food-items", FoodItemViewSet, basename="fooditem")
router.register("daily-menus", DailyMenuViewSet, basename="dailymenu")

urlpatterns = router.urls
