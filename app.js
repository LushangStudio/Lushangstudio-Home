const applicationGrid = document.querySelector("#apps");
const applicationCount = document.querySelector("#count");
const emptyMessage = document.querySelector("#empty");
const searchInput = document.querySelector("#search");

// The catalog is separate from the UI so new applications need no layout changes.
async function loadApplications() {
  try {
    const response = await fetch(new URL("apps.json", document.baseURI));
    if (!response.ok) {
      throw new Error("应用目录加载失败");
    }
    return await response.json();
  } catch (error) {
    emptyMessage.textContent = "应用目录暂时无法加载，请刷新重试。";
    console.error(error);
    return [];
  }
}

// Use textContent for catalog text rather than interpreting it as HTML.
function createTextElement(tagName, className, text) {
  const element = document.createElement(tagName);
  element.className = className;
  element.textContent = text;
  return element;
}

function createApplicationCard(application) {
  const isAvailable = application.status === "available";
  const card = document.createElement(isAvailable ? "a" : "article");
  card.className = `app ${application.color}`;

  if (isAvailable) {
    card.href = application.href;
  }

  const content = [
    ["div", "icon", application.icon],
    ["span", "category", application.tag],
    ["h3", "", application.name],
    ["h4", "", application.subtitle],
    ["p", "", application.description],
    ["span", "open", isAvailable ? "打开应用 ↗" : "准备中 · 敬请期待"],
  ];

  for (const [tagName, className, text] of content) {
    card.append(createTextElement(tagName, className, text));
  }
  return card;
}

function renderApplications(applications, query = "") {
  const normalizedQuery = query.trim().toLocaleLowerCase();
  const visibleApplications = applications.filter((application) => {
    const searchableText = [
      application.name,
      application.subtitle,
      application.description,
    ].join(" ");
    return searchableText.toLocaleLowerCase().includes(normalizedQuery);
  });

  applicationGrid.replaceChildren();
  applicationCount.textContent = applications.length;
  emptyMessage.hidden = visibleApplications.length > 0;

  for (const application of visibleApplications) {
    applicationGrid.append(createApplicationCard(application));
  }
}

const applications = await loadApplications();

// npm dev exposes the same local demonstration links as the workspace launcher.
// Production builds retain the catalog's explicit release status.
if (import.meta.env?.DEV) {
  for (const application of applications) {
    if (application.id === "leave") {
      application.status = "available";
      application.tag = "本地演示";
    }
  }
}

searchInput.addEventListener("input", (event) => {
  renderApplications(applications, event.target.value);
});
renderApplications(applications);
