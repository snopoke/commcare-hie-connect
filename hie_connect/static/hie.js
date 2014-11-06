(function() {
  var hieApp;

  hieApp = angular.module('hieApp', []);

  hieApp.controller('HieController', function($scope, $http, $window) {
      $scope.records = [];
      $scope.total = 0;
      $scope.currentPage = 0;
      $scope.numPerPage = 5;
      $scope.case = '';
      $scope.user = '';
      $scope.start = 0;
      $scope.end = 0;
      $scope.disableNext = true;

      $scope.getRecords = function() {
          var url = '/records.json';
          url += '?page=' + $scope.currentPage;
          url += '&limit=' + $scope.numPerPage;
          if ($scope.case.length) {
              url += '&case=' + $scope.case;
          }
          if ($scope.user.length) {
              url += '&user=' + $scope.user;
          }
          $http.get(url).success(function(data) {
              $scope.records = data.records;
              $scope.total = data.total;
              $scope.start = $scope.currentPage * $scope.numPerPage;
              $scope.end = $scope.start + $scope.numPerPage;
              $scope.disableNext = $scope.end >= $scope.total;
          });
      };

      $scope.previousPage = function() {
          $scope.currentPage = Math.max(0, $scope.currentPage -1);
          $scope.getRecords();
      };

      $scope.nextPage = function() {
          $scope.currentPage += 1;
          $scope.getRecords();
      };

      $scope.resetSearch = function() {
          $scope.case = '';
          $scope.user = '';
          $scope.getRecords();
      };

      $scope.getRecords();
  });

}).call(this);
