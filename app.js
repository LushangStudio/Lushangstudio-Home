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
  const card = document.createElement("a");
  card.className = `app ${application.color}`;

  card.href = application.href;

  const content = [
    ["div", "icon", application.icon],
    ["span", "category", application.tag],
    ["h3", "", application.name],
    ["span", "subtitle", application.subtitle],
    ["p", "", application.description],
  ];

  for (const [tagName, className, text] of content) {
    if (text) card.append(createTextElement(tagName, className, text));
  }
  if (application.features?.length) {
    const features = document.createElement("ul");
    features.className = "features";
    features.setAttribute("aria-label", "主要功能");
    for (const feature of application.features) {
      features.append(createTextElement("li", "", feature));
    }
    card.append(features);
  }
  card.append(createTextElement("span", "open", "打开应用 ↗"));
  return card;
}

function renderApplications(applications, query = "") {
  const normalizedQuery = query.trim().toLocaleLowerCase();
  const visibleApplications = applications.filter((application) => {
    const searchableText = [
      application.name,
      application.subtitle,
      application.description,
      ...(application.features ?? []),
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

// WebVPN wraps scripts in a regular function, so avoid top-level await.
async function initializeApplications() {
  // Visibility is a frontend preference, not an access-control boundary.
  const showAll = new URLSearchParams(window.location.search).has("showall");
  const applications = (await loadApplications()).filter(
    (application) => showAll || application.status === "released",
  );

  searchInput.addEventListener("input", (event) => {
    renderApplications(applications, event.target.value);
  });
  renderApplications(applications);
}

initializeApplications();
