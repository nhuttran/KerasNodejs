define([
    '../utils/commons',
    './ApiClient',
    'ojs/ojbootstrap',
    'knockout',
    "jquery",
    'ojs/ojknockout',
    'ojs/ojrouter',
], function(__commons, ApiClient, oj, ko, $) {
    function AuthListener() {
        self = this;
        
        self.refresh = function() {
            var params = __commons.getUrlParameters();
            if (params["ojr"] == "login") {
                return;
            }
            
            var client = new ApiClient();
            client.get("/auth/is_login", {}, true)
            .done(function(resp, textStatus, jqXHR) {
                // エラーチェック
                if (client.isResponseError(resp)) {
                    return;
                }
            });
        };
    }

    return new AuthListener();
});