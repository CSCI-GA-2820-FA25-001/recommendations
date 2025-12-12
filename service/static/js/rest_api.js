$(function () {
  // ============ UTILITIES ============

  function update_form_data(res) {
    $("#recommendation_id").val(res.id);
    $("#recommendation_name").val(res.name);
    $("#recommendation_base_product_id").val(res.base_product_id);
    $("#recommendation_recommended_product_id").val(res.recommended_product_id);
    $("#recommendation_recommendation_type").val(res.recommendation_type); // e.g., "accessory"
    $("#recommendation_status").val(res.status);                             // e.g., "active"
    $("#recommendation_likes").val(res.likes);
  }

  function clear_form_data() {
    $("#recommendation_id").val("");
    $("#recommendation_name").val("");
    $("#recommendation_base_product_id").val("");
    $("#recommendation_recommended_product_id").val("");
    $("#recommendation_recommendation_type").val("");
    $("#recommendation_status").val("");
    $("#recommendation_likes").val("");
  }

  function flash_message(msg) {
    $("#flash_message").empty().text(msg);
  }

  // ============ CREATE ============

  $("#create-btn").click(function () {
    const body = {
      name: $("#recommendation_name").val(),
      base_product_id: parseInt($("#recommendation_base_product_id").val(), 10),
      recommended_product_id: parseInt($("#recommendation_recommended_product_id").val(), 10),
      recommendation_type: $("#recommendation_recommendation_type").val(), // "accessory" | "cross_sell" | ...
      status: $("#recommendation_status").val() || "draft",
      likes: parseInt($("#recommendation_likes").val() || "0", 10)
    };

    $("#flash_message").empty();

    $.ajax({
      type: "POST",
      url: "/api/recommendations",
      contentType: "application/json",
      data: JSON.stringify(body),
    })
    .done(function (res) {
      update_form_data(res);
      flash_message("Successfully created a recommendation.");
    })
    .fail(function (res) {
      flash_message(res.responseJSON?.message || "Create failed.");
    });
  });

  // ============ UPDATE ============

  $("#update-btn").click(function () {
    const id = $("#recommendation_id").val();
    if (!id) return flash_message("Please select a recommendation to update.");

    const body = {
      name: $("#recommendation_name").val(),
      base_product_id: parseInt($("#recommendation_base_product_id").val(), 10),
      recommended_product_id: parseInt($("#recommendation_recommended_product_id").val(), 10),
      recommendation_type: $("#recommendation_recommendation_type").val(),
      status: $("#recommendation_status").val() || "draft",
      likes: parseInt($("#recommendation_likes").val() || "0", 10)
    };

    $("#flash_message").empty();

    $.ajax({
      type: "PUT",
      url: `/api/recommendations/${id}`,
      contentType: "application/json",
      data: JSON.stringify(body)
    })
    .done(function (res) {
      update_form_data(res);
      flash_message("Updated successfully.");
    })
    .fail(function (res) {
      flash_message(res.responseJSON?.message || "Update failed.");
    });
  });

  // ============ RETRIEVE (GET by id) ============

  $("#retrieve-btn").click(function () {
    const id = $("#recommendation_id").val();
    if (!id) return flash_message("Please enter an ID to retrieve.");

    $("#flash_message").empty();

    $.ajax({
      type: "GET",
      url: `/api/recommendations/${id}`,
      contentType: "application/json"
    })
    .done(function (res) {
      update_form_data(res);
      flash_message("Success");
    })
    .fail(function (res) {
      clear_form_data();
      if (res.status === 404) {
        flash_message("404 Not Found");
      } else {
        flash_message(res.responseJSON?.message || "Error");
      }
    });
  });

  // ============ LIST (GET all) ============

  $("#list-btn").click(function () {
    $("#flash_message").empty();

    $.ajax({
      type: "GET",
      url: "/api/recommendations",
      contentType: "application/json"
    })
    .done(function (res) {
      $("#search_results").empty();
      let table = '<table class="table table-striped" cellpadding="10">';
      table += '<thead><tr>';
      table += '<th>ID</th><th>Name</th><th>Base Product ID</th><th>Recommended Product ID</th>';
      table += '<th>Type</th><th>Status</th><th>Likes</th>';
      table += '</tr></thead><tbody>';

      let first = null;
      res.forEach((r, i) => {
        table += `<tr id="row_${i}">
          <td>${r.id}</td>
          <td>${r.name}</td>
          <td>${r.base_product_id}</td>
          <td>${r.recommended_product_id}</td>
          <td>${r.recommendation_type}</td>
          <td>${r.status}</td>
          <td>${r.likes}</td>
        </tr>`;
        if (i === 0) first = r;
      });

      table += '</tbody></table>';
      $("#search_results").append(table);
      if (first) update_form_data(first);
      flash_message("Success");
    })
    .fail(function (res) {
      flash_message(res.responseJSON?.message || "List failed.");
    });
  });

  // ============ DELETE ============

  $("#delete-btn").click(function () {
    const id = $("#recommendation_id").val();
    if (!id) return flash_message("Please select a recommendation to delete.");

    $("#flash_message").empty();

    $.ajax({
      type: "DELETE",
      url: `/api/recommendations/${id}`,
      contentType: "application/json"
    })
    .done(function () {
      clear_form_data();
      flash_message("Recommendation deleted.");
    })
    .fail(function () {
      flash_message("Server error while deleting.");
    });
  });

  // ============ CLEAR FORM ============

  $("#clear-btn").click(function () {
    $("#flash_message").empty();
    clear_form_data();
  });

  // ============ SEARCH (by filters your API supports) ============

  $("#search-btn").click(function () {
    const baseId = $("#recommendation_base_product_id").val();
    const relType = $("#recommendation_recommendation_type").val();
    const statusVal = $("#recommendation_status").val();

    const params = new URLSearchParams();
    if (baseId) params.set("base_product_id", baseId);       // your API also accepts product_a_id
    if (relType) params.set("recommendation_type", relType);   // maps to RecommendationType
    if (statusVal) params.set("status", statusVal);          // maps to RecommendationStatus
    // optional: params.set("sort","created_at_desc");

    $("#flash_message").empty();

    $.ajax({
      type: "GET",
      url: `/api/recommendations?${params.toString()}`,
      contentType: "application/json"
    })
    .done(function (res) {
      $("#search_results").empty();
      let table = '<table class="table table-striped" cellpadding="10">';
      table += '<thead><tr>';
      table += '<th>ID</th><th>Name</th><th>Base Product ID</th><th>Recommended Product ID</th>';
      table += '<th>Type</th><th>Status</th><th>Likes</th>';
      table += '</tr></thead><tbody>';

      let first = null;
      res.forEach((r, i) => {
        table += `<tr id="row_${i}">
          <td>${r.id}</td>
          <td>${r.name}</td>
          <td>${r.base_product_id}</td>
          <td>${r.recommended_product_id}</td>
          <td>${r.recommendation_type}</td>
          <td>${r.status}</td>
          <td>${r.likes}</td>
        </tr>`;
        if (i === 0) first = r;
      });

      table += '</tbody></table>';
      $("#search_results").append(table);
      if (first) update_form_data(first);
      flash_message("Success");
    })
    .fail(function (res) {
      flash_message(res.responseJSON?.message || "Search failed.");
    });
  });

  // ============ LIKE / DISLIKE ============

  $("#like-btn").click(function () {
    const id = $("#recommendation_id").val();
    if (!id) return flash_message("Please select a recommendation to like.");

    $("#flash_message").empty();

    $.ajax({
      type: "PUT",
      url: `/api/recommendations/${id}/like`,
      contentType: "application/json"
    })
    .done(function (res) {
      update_form_data(res);
      flash_message("Successfully liked the recommendation!");
    })
    .fail(function (res) {
      flash_message(res.responseJSON?.message || "Like failed.");
    });
  });

  $("#dislike-btn").click(function () {
    const id = $("#recommendation_id").val();
    if (!id) return flash_message("Please select a recommendation to dislike.");

    $("#flash_message").empty();

    $.ajax({
      type: "DELETE",
      url: `/api/recommendations/${id}/like`,
      contentType: "application/json"
    })
    .done(function (res) {
      update_form_data(res);
      flash_message("Successfully disliked the recommendation!");
    })
    .fail(function (res) {
      flash_message(res.responseJSON?.message || "Dislike failed.");
    });
  });
});
