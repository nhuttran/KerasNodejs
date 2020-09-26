define([
    '../models/ApiClient',
    'accUtils',
    'knockout',
    'ojs/ojpagingdataproviderview', 
    'ojs/ojarraydataprovider',
    'ojs/ojkeyset',
    'ojs/ojknockout',
    'ojs/ojselectsingle',
    'ojs/ojtable',
    'ojs/ojpagingcontrol',
    'ojs/ojbutton',
    'ojs/ojpopup',
], function(ApiClient, accUtils, ko, PagingDataProviderView, ArrayDataProvider, keySet) {
    function FaceIdListViewModel() {
        var self = this;
        var _faceStatusList = [];

        self.modelTrainStatusViewPopup = "trainStatusViewPopup";
        self.selectedFaceId = ko.observable("-1");
        self.faceIdOptions = ko.observable([]);

        self.headerColumns = [
            { headerText: "Face ID",   field: "faceId",     sortable: "enabled", resizable: "disabled" },
            { headerText: "Face Name", field: "faceName",   sortable: "enabled", resizable: "enabled"  },
            { headerText: "SEQ",       field: "seq",        sortable: "enabled", resizable: "disabled" },
            { headerText: "ステータス", field: "statusName", sortable:"disabled", resizable: "disabled" },
             {headerText: "画像",      field: "faceBinary", sortable:"disabled", resizable: "disabled" }
        ];

        self.selectedFace = ko.observable({row: new keySet.KeySetImpl(), column: new keySet.KeySetImpl()});
        var _pagingDataFaces = new PagingDataProviderView(new ArrayDataProvider([], { idAttribute: "faceId,seq" }));
        self.pagingDataFaces = ko.observable(_pagingDataFaces);

        self.connected = () => {
            accUtils.announce('Customers page loaded.', 'assertive');
            document.title = "顔ＩＤ一覧";
        };

        /**
         * Optional ViewModel method invoked after the View is disconnected from the DOM.
         */
        self.disconnected = () => {
            // Implement if needed
        };

        self.transitionCompleted = () => {
            // Implement if needed
        };

        /**
         * 検索ボタン押下時のFaceID情報取得ハンドラ
         */
        self.searchBtnClick = function(data, event) {
            var client = new ApiClient();
            client.addData("loginId", sessionStorage.getItem("loginId"));
            client.addData("faceId", self.selectedFaceId());
            client.post("/searchDetectFaceList", false)
            .done(function(resp, textStatus, jqXHR) {
                // エラーチェック
                if (client.isResponseError(resp)) {
                    return;
                }
                var faceInfoData = Enumerable.from(resp.detectFaceList)
                .select(function(item) {
                    var statusName = Enumerable.from(_faceStatusList)
                    .where(function(statusInfo) {
                        return item.faceStatusKbn == statusInfo.statusKbn && statusInfo.language == "ja";
                    }).select(function(statusInfo) { return statusInfo.statusName }).toArray()[0];

                    return {faceId: item.faceId, faceName: item.faceName, seq: item.seq, statusName: statusName,
                            faceBinary: "data:image/jpeg;base64," + item.faceBinary};
                }).toArray();
                var pagingDataFaces = new PagingDataProviderView(new ArrayDataProvider(faceInfoData, { idAttribute: "faceId,seq" }));
                self.pagingDataFaces(pagingDataFaces);
            });
        };

        /**
         * 学習開始ボタン押下ハンドラ
         */
        self.startTrainBtnClick = function(data, event) {
            var client = new ApiClient();
            client.addData("loginId", sessionStorage.getItem("loginId"));
            client.post("/startTrain", false)
            .done(function(resp, textStatus, jqXHR) {
                // エラーチェック
                if (client.isResponseError(resp)) {
                    return;
                }
                if (resp.trainCount > 0) {
                    alert("顔学習が始めました。学習ステータス画面で学習ステータスが確認できます。");
                } else {
                    alert("学習データがありません。学習ステータス画面で学習ステータスが確認できます。");
                }
            });
        }

        /**
         * 学習停止ボタン押下ハンドラ
         */
        self.stopTrainBtnClick = function(data, event) {
            alert("未実装");
        }

        /**
         * 学習ステータスボタン押下ハンドラ
         */
        self.trainStatusBtnClick = function(data, event) {
            var viewTrainStatus = ko.dataFor(document.querySelector("#view-train-status"));
            viewTrainStatus.request("trainStatusPopup");
        }

        /**
         * 初期表示
         */
        function initialize() {
            var faceStatusClient = new ApiClient();
            faceStatusClient.addData("loginId", sessionStorage.getItem("loginId"));
            faceStatusClient.post("/searchFaceStatus", false)
            .done(function(resp, textStatus, jqXHR) {
                // エラーチェック
                if (faceStatusClient.isResponseError(resp)) {
                    return;
                }
                _faceStatusList = Enumerable.from(resp.faceStatusList)
                .select(function(item) {
                    return {statusKbn: item.faceStatusKbn, language: item.language, statusName: item.faceStatusName};
                }).toArray();
            });

            var faceIdsClient = new ApiClient();
            faceIdsClient.addData("loginId", sessionStorage.getItem("loginId"));
            faceIdsClient.post("/searchFaceIds", false)
            .done(function(resp, textStatus, jqXHR) {
                // エラーチェック
                if (faceIdsClient.isResponseError(resp)) {
                    return;
                }
                var __dataTable = [{value: "-1", label: "指定なし"}]
                Enumerable.from(resp.faceIdList)
                .forEach(function (item) {
                    __dataTable.push({value: item.faceId, label: item.faceName})
                });
                self.faceIdOptions(new ArrayDataProvider(__dataTable, { keyAttributes: "value" }));
            });
        }

        initialize()
    }

    return new FaceIdListViewModel();
});