document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadStats();

        loadCategories();

        loadCountries();

        loadCreators();

    }
);


/* -------------------------
   STATISTICS
------------------------- */

async function loadStats() {

    const response =
        await fetch("/api/stats");

    const data =
        await response.json();


    document.getElementById(
        "totalCreators"
    ).textContent =
        data.total_creators.toLocaleString();


    document.getElementById(
        "totalCategories"
    ).textContent =
        data.total_categories.toLocaleString();


    document.getElementById(
        "totalCountries"
    ).textContent =
        data.total_countries.toLocaleString();

}


/* -------------------------
   CATEGORIES
------------------------- */

async function loadCategories() {

    const response =
        await fetch("/api/categories");

    const categories =
        await response.json();


    const select =
        document.getElementById(
            "categoryFilter"
        );


    categories.forEach(
        function (category) {

            const option =
                document.createElement(
                    "option"
                );

            option.value = category;

            option.textContent = category;

            select.appendChild(option);

        }
    );

}


/* -------------------------
   COUNTRIES
------------------------- */

async function loadCountries() {

    const response =
        await fetch("/api/countries");

    const countries =
        await response.json();


    const select =
        document.getElementById(
            "countryFilter"
        );


    countries.forEach(
        function (country) {

            const option =
                document.createElement(
                    "option"
                );

            option.value = country;

            option.textContent = country;

            select.appendChild(option);

        }
    );

}


/* -------------------------
   SEARCH
------------------------- */

async function searchCreators() {

    const search =
        document.getElementById(
            "searchInput"
        ).value;


    const category =
        document.getElementById(
            "categoryFilter"
        ).value;


    const country =
        document.getElementById(
            "countryFilter"
        ).value;


    const params =
        new URLSearchParams();


    if (search) {

        params.append(
            "search",
            search
        );

    }


    if (category) {

        params.append(
            "category",
            category
        );

    }


    if (country) {

        params.append(
            "country",
            country
        );

    }


    const response =
        await fetch(
            "/api/creators?" +
            params.toString()
        );


    const creators =
        await response.json();


    displayCreators(creators);

}


/* -------------------------
   LOAD CREATORS
------------------------- */

async function loadCreators() {

    const response =
        await fetch(
            "/api/creators"
        );


    const creators =
        await response.json();


    displayCreators(creators);

}


/* -------------------------
   DISPLAY
------------------------- */

function displayCreators(
    creators
) {

    const grid =
        document.getElementById(
            "creatorGrid"
        );


    grid.innerHTML = "";


    if (creators.length === 0) {

        grid.innerHTML =
            "<p>No creators found.</p>";

        return;

    }


    creators.forEach(
        function (creator, index) {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "creator-card";


            let image;


            if (
                creator.profile_picture_url
            ) {

                image = `
                    <img
                        src="${creator.profile_picture_url}"
                        class="creator-image"
                    >
                `;

            } else {

                image = `
                    <div
                        class="creator-placeholder"
                    >
                        ${
                            creator.channel_name
                                ? creator.channel_name[0]
                                : "?"
                        }
                    </div>
                `;

            }


            card.innerHTML = `

                ${image}

                <div class="creator-content">

                    <div class="rank">
                        #${creator.rank || index + 1}
                    </div>

                    <h3>
                        ${creator.channel_name || "Unknown"}
                    </h3>

                    <p>
                        ${creator.country || "Unknown"}
                    </p>

                    <div class="category">
                        ${creator.topic_groups || "Unknown"}
                    </div>

                    <div class="creator-stats">

                        <span>
                            👥
                            ${formatNumber(
                                creator.subscribers
                            )}
                        </span>

                        <span>
                            👁
                            ${formatNumber(
                                creator.views
                            )}
                        </span>

                    </div>

                    <a
                        href="/creator/${creator.id}"
                    >
                        View Profile →
                    </a>

                </div>
            `;


            grid.appendChild(card);

        }
    );

}


/* -------------------------
   NUMBER FORMAT
------------------------- */

function formatNumber(number) {

    if (!number) {
        return "0";
    }


    number =
        Number(number);


    if (
        number >= 1000000000
    ) {

        return (
            (number / 1000000000)
            .toFixed(1) + "B"
        );

    }


    if (
        number >= 1000000
    ) {

        return (
            (number / 1000000)
            .toFixed(1) + "M"
        );

    }


    if (
        number >= 1000
    ) {

        return (
            (number / 1000)
            .toFixed(1) + "K"
        );

    }


    return number.toString();

}
