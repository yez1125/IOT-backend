function initializeFeatures(features, recommendedFeatures) {
  const featuresContainer = document.getElementById("featuresContainer");
  featuresContainer.innerHTML = '<div class="features-title">可用特徵</div>';

  features.forEach((feature) => {
    const div = document.createElement("div");
    div.className = "feature-item";
    const isRecommended = recommendedFeatures.includes(feature);

    if (isRecommended) {
      div.classList.add("recommended");
    }

    div.innerHTML = `
            <label>
                <input type="checkbox" name="features[]" value="${feature}" 
                       ${isRecommended ? "checked" : ""}>
                <span>${feature}</span>
            </label>
        `;

    featuresContainer.appendChild(div);
  });
}

function setupFeatureListeners() {
  document.querySelectorAll('input[name="parkType"]').forEach((radio) => {
    radio.addEventListener("change", function () {
      const parkType = this.value;
      const recommendedFeatures = PARK_TYPE_FEATURES[parkType];

      const allFeatureCheckboxes = document.querySelectorAll(
        'input[name="features[]"]'
      );
      allFeatureCheckboxes.forEach((checkbox) => {
        const featureItem = checkbox.closest(".feature-item");
        checkbox.checked = recommendedFeatures.includes(checkbox.value);
        featureItem.classList.toggle(
          "recommended",
          recommendedFeatures.includes(checkbox.value)
        );
      });
    });
  });
}
