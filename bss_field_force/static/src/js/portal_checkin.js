// Alternative approach - Direct DOM binding
$(document).ready(function () {
    console.log("🚀 Direct DOM binding loaded");

    function handleAction(action) {
        console.log("➡️ Direct action triggered:", action);

        if (!navigator.geolocation) {
            alert("Geolocation not supported.");
            return;
        }

        navigator.geolocation.getCurrentPosition(function (pos) {
            let lat = pos.coords.latitude;
            let lon = pos.coords.longitude;

            console.log("📍 Got location:", lat, lon);

            // Get CSRF token from meta tag or form
            let csrfToken = $('input[name="csrf_token"]').val() ||
                $('meta[name="csrf-token"]').attr('content') ||
                odoo.csrf_token;

            $.ajax({
                url: '/create/field/force/rec',
                type: 'POST',
                data: {
                    lat: lat,
                    lon: lon,
                    action: action,
                    csrf_token: csrfToken
                },
                success: function (res) {
                    console.log("✅ Server response:", res);
                    if (res.success) {
                        alert(action + " saved at: " + res.address);
                        window.location.reload();
                    } else {
                        alert("Error saving record.");
                    }
                },
                error: function (xhr, status, error) {
                    console.error("❌ AJAX error:", status, error, xhr.responseText);
                    alert("Error: " + xhr.status + " - " + xhr.responseText);
                }

            });

        }, function (error) {
            console.error("📍 Geolocation error:", error);
            alert("Unable to fetch location.");
        });
    }

    // Bind click events directly
    $(document).on('click', '.o-btn-checkin', function (e) {
        console.log("🔘 Check In clicked (direct binding)!");
        e.preventDefault();
        handleAction('checkin');
    });

    $(document).on('click', '.o-btn-checkout', function (e) {
        console.log("🔘 Check Out clicked (direct binding)!");
        e.preventDefault();
        handleAction('checkout');
    });
});