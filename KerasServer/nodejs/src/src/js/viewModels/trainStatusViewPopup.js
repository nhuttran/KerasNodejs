define([
    "../utils/CodeUtils",
    "../utils/commons",
    '../models/ApiClient',
    "../models/Popup",
    'knockout',
    'ojs/ojknockout',
    'ojs/ojgauge',
    'ojs/ojlabel',
    'ojs/ojpopup',
    'ojs/ojdialog',
],function(CodeUtils, commons, ApiClient, Popup, ko) {
    function TrainStatusViewPopup() {
        var self = this;

        self.popup = new Popup("view-train-status");
        self.title = ko.observable("学習ステータス");

        var updateTrainStatus = function() {
            var trainKbn = "0";
            var client = new ApiClient();
            client.addData("loginId", sessionStorage.getItem("loginId"));
            client.post("/getTrainStatus", false)
            .done(function(resp, textStatus, jqXHR) {
                // エラーチェック
                if (client.isResponseError(resp)) {
                    return;
                }
                
                Enumerable.from(resp.trainStatusList)
                .forEach(function(item) {
                    var curPercent = (item.currentEpoch/item.epochs) * 100;
                    var trainStatusName = commons.getTrainStatusName(parseInt(item.status));
                    if (item.status == CodeUtils.TRAIN_STATUS.FINISHED) {
                        curPercent = 100;
                    }
                    switch(parseInt(item.trainKbn)) {
                        case CodeUtils.TRAIN_KIND.VGG16:
                            self.vgg16StatusName(trainStatusName);
                            self.vgg16CurrentStatus(curPercent); break;
                        case CodeUtils.TRAIN_KIND.VGG19:
                            self.vgg19StatusName(trainStatusName);
                            self.vgg19CurrentStatus(curPercent); break;
                        case CodeUtils.TRAIN_KIND.VGG_FACE:
                            self.vggFaceStatusName(trainStatusName);
                            self.vggFaceCurrentStatus(curPercent); break;
                    }
                });
            });
        }

        self.vgg16StatusName = ko.observable("");
        self.vgg16CurrentStatus = ko.observable(0);
        self.vgg19StatusName = ko.observable("");
        self.vgg19CurrentStatus = ko.observable(0);
        self.vggFaceStatusName = ko.observable("");
        self.vggFaceCurrentStatus = ko.observable(0);
        self.customSvgStyle = { fill: 'url(' + document.URL + '#pattern)' }

        var updateStatusTimer = null;
        function startUpdateStatusTimer() {
            var index = 0;
            // 1分毎に学習ステータス更新を繰り返す。
            updateStatusTimer = setInterval(function(){
                index++;
                console.log("学習ステータス更新" + index);
                updateTrainStatus();
            } , 60000);
        }

        function stopUpdateStatusTimer() {
            clearInterval(updateStatusTimer);
        }

        function initialize() {
            startUpdateStatusTimer();
            updateTrainStatus();
        }

        self.request = function (popupId) {
            initialize();
            self.popup.popupOpen();
        }

        self.popupClose = function () {
            stopUpdateStatusTimer();
            self.popup.popupClose()
        }
    }

    return new TrainStatusViewPopup();
});