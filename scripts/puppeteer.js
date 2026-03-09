import puppeteer from "puppeteer";
import fs from "node:fs";

const browser = await puppeteer.launch();

try {

  const targetUrls =["https://messervices.cyber.gouv.fr/",
                      "https://messervices.cyber.gouv.fr/nis2",
                      "https://demainspecialiste.cyber.gouv.fr/",
                      "https://demainspecialiste.cyber.gouv.fr/cyber-en-jeux"  ];
  for (const targetUrl of targetUrls){

      const page = await browser.newPage();
      await page.setViewport({ width: 1080, height: 1024 });

      let response = null;
      let navigationTimedOut = false;

      try {
        response = await page.goto(targetUrl, {
          waitUntil: "domcontentloaded",
          timeout: 2000,
        });
      } catch (error) {
        if (error?.name !== "TimeoutError") {
          throw error;
        }
        navigationTimedOut = true;
      }

      await page.waitForSelector("body", { timeout: 2000 });

      if (navigationTimedOut) {
        console.warn("Navigation > 2000ms: on continue avec le DOM deja charge.");
      } else if (response) {
        console.log(`HTTP status: ${response.status()}`);
      }

      await page
        .waitForFunction(
          () => document.body && document.body.innerText.includes("Se lancer en cyber"),
          { timeout: 2000 }
        )
        .catch(() => {
        });

      await page.evaluate(() => {
        const ELEMENT_NODE = Node.ELEMENT_NODE;
        const TEXT_NODE = Node.TEXT_NODE;
        const COMMENT_NODE = Node.COMMENT_NODE;
        const DOCUMENT_FRAGMENT_NODE = Node.DOCUMENT_FRAGMENT_NODE;

        function copyHostAttributes(source, target) {
          for (const attr of Array.from(source.attributes)) {
            if (
              attr.name === "id" ||
              attr.name === "class" ||
              attr.name.startsWith("aria-") ||
              attr.name.startsWith("data-")
            ) {
              target.setAttribute(attr.name, attr.value);
              continue;
            }
            target.setAttribute(`data-host-${attr.name}`, attr.value);
          }
        }

        function expandNode(node) {
          if (node.nodeType === TEXT_NODE) {
            return document.createTextNode(node.textContent ?? "");
          }

          if (node.nodeType === COMMENT_NODE) {
            return document.createComment(node.textContent ?? "");
          }

          if (node.nodeType === DOCUMENT_FRAGMENT_NODE) {
            const fragment = document.createDocumentFragment();
            for (const child of Array.from(node.childNodes)) {
              const expandedChild = expandNode(child);
              if (expandedChild) {
                fragment.appendChild(expandedChild);
              }
            }
            return fragment;
          }

          if (node.nodeType !== ELEMENT_NODE) {
            return null;
          }

          const element = /** @type {Element} */ (node);

          // Resolve distributed content for <slot> during flattening.
          if (element.tagName.toLowerCase() === "slot") {
            const fragment = document.createDocumentFragment();
            const assigned = element.assignedNodes({ flatten: true });
            const sourceNodes = assigned.length > 0 ? assigned : Array.from(element.childNodes);

            for (const source of sourceNodes) {
              const expandedSource = expandNode(source);
              if (expandedSource) {
                fragment.appendChild(expandedSource);
              }
            }

            return fragment;
          }

          if (element.shadowRoot) {
            const wrapper = document.createElement("div");
            wrapper.setAttribute("data-shadow-host", element.tagName.toLowerCase());
            copyHostAttributes(element, wrapper);

            for (const child of Array.from(element.shadowRoot.childNodes)) {
              const expandedChild = expandNode(child);
              if (expandedChild) {
                wrapper.appendChild(expandedChild);
              }
            }

            return wrapper;
          }

          const clone = element.cloneNode(false);
          for (const child of Array.from(element.childNodes)) {
            const expandedChild = expandNode(child);
            if (expandedChild) {
              clone.appendChild(expandedChild);
            }
          }

          return clone;
        }

        const newBody = document.createElement("body");
        for (const child of Array.from(document.body.childNodes)) {
          const expandedChild = expandNode(child);
          if (expandedChild) {
            newBody.appendChild(expandedChild);
          }
        }

        document.body.replaceWith(newBody);

        document.querySelectorAll("script").forEach((scriptEl) => scriptEl.remove());
      });

      const html = await page.content();
      const fileName = targetUrl
        .replace(/^https?:\/\//, '')
        .replace(/\//g, '_')
        .replace(/[?#:*"<>|]/g, '_') + '.html';
      fs.writeFileSync(fileName, html, "utf-8");
      console.log(`Saved: ${fileName}`);

  }
} finally {
  await browser.close();
}
