define([
    "./CodeUtils",
    "jquery"
], function(CodeUtils, ko, $) {
    var parseUrlParameters = function (url) {
        var query = {};
        if (url == null || url == '') {
            return query;
        }

        var queryString = url.replace(/^(.*\?)?/g, '');
        if (queryString == '') {
            return query;
        }

        var params = queryString.split('&');
        for (var i = 0; i < params.length; i++) {
            var param = params[i].split('=');
            if (param.length < 2 || !param[0] || !param[1]) {
                continue;
            }
            query[param[0]] = param[1];
        }
        return query;
    };

    var commons = {
        // 指定の学習ステータスにより学習ステータス名を取得する
        getTrainStatusName: function(train_status) {
            var trainStatusName = "";
            switch(train_status){
                case CodeUtils.TRAIN_STATUS.SENDED:
                    trainStatusName = "依頼済"; break;
                case CodeUtils.TRAIN_STATUS.READY:
                    trainStatusName = "学習準備"; break;
                case CodeUtils.TRAIN_STATUS.RUNNING:
                    trainStatusName = "学習中"; break;
                case CodeUtils.TRAIN_STATUS.FINISHED:
                    trainStatusName = "学習完了"; break;
                case CodeUtils.TRAIN_STATUS.APPLYING:
                    trainStatusName = "適用中"; break;
                case CodeUtils.TRAIN_STATUS.CANCELED:
                    trainStatusName = "キャンセル済"; break;
                case CodeUtils.TRAIN_STATUS.RESENDED:
                    trainStatusName = "再依頼済"; break;
                case CodeUtils.TRAIN_STATUS.ERROR:
                    trainStatusName = "エラー"; break;
                default:
                    trainStatusName = "未依頼";
            }
            return trainStatusName;
        },
        // リクエストURL用のパラメータリストを接合する
        createQueryString: function (queryParams) {
            var queryString = Enumerable.from(queryParams).select(
                function (x) { return x.key + '=' + encodeURIComponent(x.value); }
            ).toArray().join('&');
            return queryString.length === 0 ? '' : '?' + queryString;
        },
        // リクエストURLからパラメータを取得する
        getUrlParameters: function () {
            return parseUrlParameters(document.location.search);
        }
    }

    return commons;
});