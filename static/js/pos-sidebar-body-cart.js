$(document).ready(function() {
    // Event listener for clicking on Add to Cart button
    $('.add-to-cart').off('click').on('click', function(e) {
        e.preventDefault();
        
        // Retrieve product details from data attributes
        var productName = $(this).closest('.pos-product').find('.title').text();
        var productPriceString = $(this).closest('.pos-product').find('.price').text().replace('$', '');
        var productPrice = parseFloat(productPriceString); // Convert price to float

        // Check if the parsed price is a valid number
        if (!isNaN(productPrice)) {
            var productImageUrl = $(this).data('image-url'); // Retrieve image URL from data attribute 
            
            // Check if the product already exists in the cart
            var existingProduct = $('#newOrderTab').find('.pos-order-product:contains("' + productName + '")');
            if (existingProduct.length > 0) {
                // Update quantity and total price
                var quantityInput = existingProduct.find('input[type="text"]');
                var currentQuantity = parseInt(quantityInput.val());
                quantityInput.val(currentQuantity + 1); // Increase quantity by 1
                updateTotalPrice(existingProduct, currentQuantity + 1);
            } else {
                // Append the product to the cart sidebar
                $('#newOrderTab').append(
                    `<div class="pos-order">
                        <div class="pos-order-product">
                            <div class="img" style="background-image: url('{{ base_static_url }}uploaded_files/${productImageUrl}')"></div>
                            <div class="flex-1">
                                <div class="h6 mb-1">${productName} Pizza</div>
                                <div class="small">$${productPrice.toFixed(2)}</div>
                                <div class="d-flex">
                                    <a href="#" class="btn btn-secondary btn-sm decrease-quantity"><i class="fa fa-minus"></i></a>
                                    <input type="text" class="quantity form-control w-50px form-control-sm mx-2 bg-white bg-opacity-25 bg-white bg-opacity-25 text-center" value="01">
                                    <a href="#" class="btn btn-secondary btn-sm increase-quantity"><i class="fa fa-plus"></i></a>
                                </div>
                            </div>
                        </div>
                        <div class="pos-order-price d-flex flex-column">
                            <div class="flex-1">$${productPrice.toFixed(2)}</div>
                            <div class="text-end">
                                <a href="#" class="btn btn-default btn-sm delete-item-cart"><i class="fa fa-trash"></i></a>
                            </div>
                        </div>
                    </div>`
                );
            }
            // Calculate and update subtotal
            calculateSubtotal();
        }
    });

    // Event listener for quantity increase
    $(document).on('click', '.increase-quantity', function(e) {
        e.preventDefault();
        var quantityInput = $(this).closest('.pos-order-product').find('input[type="text"]');
        var currentQuantity = parseInt(quantityInput.val());
        quantityInput.val(currentQuantity + 1); // Increase quantity by 1
        updateTotalPrice($(this).closest('.pos-order-product'), currentQuantity + 1);
        // Calculate and update subtotal
        calculateSubtotal();
    });

    // Event listener for quantity decrease
    $(document).on('click', '.decrease-quantity', function(e) {
        e.preventDefault();
        var quantityInput = $(this).closest('.pos-order-product').find('input[type="text"]');
        var currentQuantity = parseInt(quantityInput.val());
        // Prevent decreasing quantity below 1
        if (currentQuantity > 1) {
            quantityInput.val(currentQuantity - 1); // Decrease quantity by 1
            updateTotalPrice($(this).closest('.pos-order-product'), currentQuantity - 1);
        }
        // Calculate and update subtotal
        calculateSubtotal();
    });

    // Event listener for quantity change
    $(document).on('change', '.quantity', function() {
        var quantity = parseInt($(this).val());
        updateTotalPrice($(this).closest('.pos-order-product'), quantity);
        // Calculate and update subtotal
        calculateSubtotal();
    });

    // Event listener for deleting item from cart
    $(document).on('click', '.delete-item-cart', function(e) {
        e.preventDefault();
        $(this).closest('.pos-order').remove(); // Remove the item from the DOM
        // Calculate and update subtotal
        calculateSubtotal();
    });

    // Function to update the total price based on quantity
    function updateTotalPrice(productElement, quantity) {
        var productPrice = parseFloat(productElement.find('.small').text().replace('$', ''));
        var totalPriceElement = productElement.closest('.pos-order').find('.pos-order-price .flex-1');
        totalPriceElement.text('$' + (quantity * productPrice).toFixed(2));
    }

    // Function to calculate and update the subtotal
    function calculateSubtotal() {
        var subtotal = 0;
        var total = 0;
        $('.pos-order').each(function() {
            var priceText = $(this).find('.pos-order-price .flex-1').text().trim().substring(1); // Remove the dollar sign and trim whitespace
            var price = parseFloat(priceText);
            subtotal += price;
            total += price;
        });
        $('#Subtotal').text('$' + subtotal.toFixed(2));
        $('#Total').text('$' + total.toFixed(2));
    }
});