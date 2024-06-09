## Inspiration
The local small businesses, a food pantry, and a thrift store are currently spending thousands of dollars a month to manage their inventory, which is putting them at risk of going out of business. This past school year, our school offered a solution for inventory management at a lower cost. However, due to the limited time before the school year ended, we couldn't complete the project. It makes perfect sense to develop it sooner rather than later, so we can present a working prototype or product to the local food pantry and thrift store to help them stay in business.

## What It Does
**Login Page**  
The store owner can log in with their credentials and create an account. After successfully logging in, they are redirected to the dashboard.

**Dashboard**  
The dashboard displays the products in the inventory, which can be updated or deleted. Below the products, the locations are listed, representing store locations with their names, which can also be updated or deleted.

**Products**  
The products section allows the store owner to create a new product and assign a purchase and selling price to it. The product can be updated or deleted later.

**Locations**  
The locations section allows the store owner to create a new store location that can be updated or deleted. For simplicity, customers are treated as locations.

**Movements**  
The movements section is designed for the user to move products to/from stores to efficiently manage their inventory. Like the products and locations, movements can be updated.

**Product Balance Report**  
This section displays the current inventory of products with their associated locations.

**Revenue Report**  
This section shows how much money the store owner has made from selling the products. Additionally, it displays the products and the quantities sold. The store owner can print a receipt of the revenue made.

**Add to Cart Feature**  
The store owner enters the products the customer chose to buy. They can select the available products in their respective locations and their quantities. The price and tax are dynamically updated each time a product is selected or its quantity is changed. At the bottom, there is a print receipt feature like in the revenue report section and a Checkout button.

## How We Built It
We built the website using the Flask framework in Python. The webpages were created in HTML, and Flask was used for URL routing and the entire backend. To create a satisfying dynamic webpage, we used JavaScript and Ajax to facilitate communication between the frontend and backend. The storage of products, movements, and locations is done in PKL files.

## What's Next for StoreSync Inventory Manager
We may transition from PKL files to using SQL databases for better security. We also plan to add payment forms and images associated with products. Additionally, we aim to host the server and purchase a domain name for the website to make it accessible globally.
