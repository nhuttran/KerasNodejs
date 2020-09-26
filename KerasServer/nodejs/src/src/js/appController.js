define([
  './models/AuthListener',
  'knockout',
  'ojs/ojmodule-element-utils',
  'ojs/ojknockouttemplateutils',
  'ojs/ojcorerouter',
  'ojs/ojmodulerouter-adapter',
  'ojs/ojknockoutrouteradapter',
  'ojs/ojurlparamadapter',
  'ojs/ojresponsiveutils',
  'ojs/ojresponsiveknockoututils',
  'ojs/ojarraydataprovider',
  'ojs/ojoffcanvas',
  'ojs/ojmodule-element',
  'ojs/ojknockout'],
  function(authListener, ko, moduleUtils, KnockoutTemplateUtils, CoreRouter, ModuleRouterAdapter, KnockoutRouterAdapter, UrlParamAdapter, ResponsiveUtils, ResponsiveKnockoutUtils, ArrayDataProvider, OffcanvasUtils) {
     function ControllerViewModel() {
      var self = this;
      self.authListener = authListener;

      self.KnockoutTemplateUtils = KnockoutTemplateUtils;
      self.isDisplayMenu = ko.observable(true);
      self.autoDisplayMenu = ko.computed(function () {
        var loginId = sessionStorage.getItem("loginId");
        self.isDisplayMenu(loginId != null);
      });

      // Handle announcements sent when pages change, for Accessibility.
      self.manner = ko.observable('polite');
      self.message = ko.observable();
      announcementHandler = (event) => {
        self.message(event.detail.message);
        self.manner(event.detail.manner);
      };

      document.getElementById('globalBody').addEventListener('announce', announcementHandler, false);

      // Media queries for repsonsive layouts
      const smQuery = ResponsiveUtils.getFrameworkQuery(ResponsiveUtils.FRAMEWORK_QUERY_KEY.SM_ONLY);
      self.smScreen = ResponsiveKnockoutUtils.createMediaQueryObservable(smQuery);
      const mdQuery = ResponsiveUtils.getFrameworkQuery(ResponsiveUtils.FRAMEWORK_QUERY_KEY.MD_UP);
      self.mdScreen = ResponsiveKnockoutUtils.createMediaQueryObservable(mdQuery);

      let navData = [
        { path: "", redirect: 'userHome' },
        { path: "login", detail: { label: "ログイン", iconClass: "oj-ux-ico-bar-chart", isDisplay: false } },
        { path: "userHome", detail: { label: "ユーザーホーム", iconClass: "oj-ux-ico-bar-chart", isDisplay: true } },
        { path: "faceIdList", detail: { label: "Face ID一覧", iconClass: "oj-ux-ico-fire", isDisplay: true } },
        { path: "logout", detail: { label: "ログアウト", iconClass: "oj-ux-ico-information-s", isDisplay: true } },
        { path: "customers", detail: { label: "Face ID設定情報", iconClass: "oj-ux-ico-contact-group", isDisplay: false } },
      ];

      // Router setup
      let router = new CoreRouter(navData, {
        urlAdapter: new UrlParamAdapter()
      });
      router.sync();
      self.moduleAdapter = new ModuleRouterAdapter(router);
      self.selection = new KnockoutRouterAdapter(router);
      // Setup the navDataProvider with the routes, excluding the first redirected
      // route.
      self.navDataProvider = new ArrayDataProvider(navData.slice(1), {keyAttributes: "path"});

      // Drawer
      // Close offcanvas on medium and larger screens
      self.mdScreen.subscribe(() => {OffcanvasUtils.close(self.drawerParams);});
      self.drawerParams = {
        displayMode: 'push',
        selector: '#navDrawer',
        content: '#pageContent'
      };
      // Called by navigation drawer toggle button and after selection of nav drawer item
      self.toggleDrawer = () => {
        self.navDrawerOn = true;
        return OffcanvasUtils.toggle(self.drawerParams);
      }

     }

     return new ControllerViewModel();
  }
);
