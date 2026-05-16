// dependency-cruiser config — hexagonal layering + BC isolation для stage-3-hexagonal.
//
// 4 hard rules:
//   1. domain не імпортує infra (ні свого BC, ні чужого)
//   2. domain не імпортує app
//   3. app не імпортує infra
//   4. cross-BC імпорти заборонені, окрім notifications/infra/events → інші BC domain
//
// shared/ — завжди дозволений. main wiring (src/index.ts) не аналізується (excluded).

/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    // -------------------------------------------------------------------
    // Layered rules per BC: domain → app/infra заборонено, app → infra заборонено
    // -------------------------------------------------------------------
    {
      name: "domain-no-infra",
      comment:
        "Domain не імпортує infra (ні свого BC, ні чужого). Це порушує hexagonal: domain не знає про БД, HTTP, бібліотеки.",
      severity: "error",
      from: { path: "^src/[^/]+/domain(/|$)" },
      to: { path: "^src/[^/]+/infra(/|$)" },
    },
    {
      name: "domain-no-app",
      comment:
        "Domain не імпортує app. Domain — фундамент, app тримає use cases і залежить від domain, не навпаки.",
      severity: "error",
      from: { path: "^src/[^/]+/domain(/|$)" },
      to: { path: "^src/[^/]+/app(/|$)" },
    },
    {
      name: "app-no-infra",
      comment:
        "App не імпортує infra. Use cases говорять з infra тільки через interfaces, оголошені в domain (Repository, Sender etc).",
      severity: "error",
      from: { path: "^src/[^/]+/app(/|$)" },
      to: { path: "^src/[^/]+/infra(/|$)" },
    },

    // -------------------------------------------------------------------
    // Cross-BC isolation
    // -------------------------------------------------------------------
    // Якщо файл з BC X (не з notifications/infra/events) імпортує файл з BC Y,
    // де X != Y — це порушення. shared/ дозволений завжди (rule не спрацьовує,
    // бо `to.path` обмежений `^src/(auth|catalog|commerce|billing|notifications)/`).
    {
      name: "no-cross-context",
      comment:
        "BC не імпортують один одного напряму. Cross-BC комунікація — через shared/events.Bus. " +
        "Виняток: notifications/infra/events підписується на чужі domain events і має право імпортувати " +
        "<other-bc>/domain. Усі інші cross-BC імпорти — порушення.",
      severity: "error",
      from: {
        path: "^src/(auth|catalog|commerce|billing|notifications)/(.+)",
        pathNot: "^src/notifications/infra/events/",
      },
      to: {
        path: "^src/(auth|catalog|commerce|billing|notifications)/",
        // Дозволяємо файлам того самого BC імпортувати один одного
        // (наприклад, src/auth/app/* імпортує src/auth/domain/*).
        pathNot: "^src/$1/",
      },
    },

    // notifications/infra/events МОЖЕ імпортувати інші BC, АЛЕ тільки domain.
    // Заборона на імпорт чужих app/infra — навіть для events subscriber.
    {
      name: "events-only-foreign-domain",
      comment:
        "notifications/infra/events має право імпортувати чужі BC, але тільки domain (event types). " +
        "Імпорт чужих app/ або infra/ — порушення BC isolation.",
      severity: "error",
      from: { path: "^src/notifications/infra/events/" },
      to: {
        path: "^src/(auth|catalog|commerce|billing)/(app|infra)(/|$)",
      },
    },
  ],

  options: {
    doNotFollow: { path: "node_modules" },
    tsConfig: { fileName: "tsconfig.json" },
    // Detect type-only imports теж — інакше `import type {Subscription} from ...`
    // не ловиться як cross-BC violation. Ловимо через runtime + compile-time graph.
    tsPreCompilationDeps: true,
    // Виключаємо bootstrap — він wiring layer (єдиний легітимний point, де
    // імпортуються всі BC модулі).
    exclude: { path: "(^src/index\\.ts$|node_modules)" },
    enhancedResolveOptions: {
      exportsFields: ["exports"],
      conditionNames: ["import", "require", "node", "default"],
    },
  },
};
