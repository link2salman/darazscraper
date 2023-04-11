import scrapy
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
import json

daraz_csv = "products.csv"


class DarazbotSpider(scrapy.Spider):
    name = "darazbot"
    allowed_domains = ["www.daraz.pk"]

    custom_settings = {
        'FEEDS': {
            daraz_csv: {
                'format': 'csv',
                'encoding': 'utf-8',

            }}
    }

    ransom_user_agent = True

    def start_requests(self):
        yield SplashRequest(url="https://www.daraz.pk/mens-t-shirts/?spm=a2a0e.pdp.breadcrumb.5.375b6A1B6A1BlL&page=1", callback=self.all_products)

    def all_products(self, response):
        name_check = Selector(text=response.body).css('script').getall() if Selector(text=response.body).css('script').getall() else False
        if name_check:
            all_product_data = name_check[3].replace("<script>window.pageData=", "").replace("</script>", "")
            products_json = json.loads(all_product_data)
            products = products_json["mods"]["listItems"]
            for itr in products:
                yield SplashRequest(url=response.urljoin(itr["productUrl"]), callback=self.product_detail)

        if name_check:
            if "&page=" in response.url:
                sliced = response.url.split("&page=")
                page_number = int(sliced[1])
                new_url = sliced[0] + "&page=" + str(page_number + 1)
                yield SplashRequest(url=new_url, callback=self.all_products)

        # yield {
        #     "product_name": itr["name"],
        #     "product_orignal_price": itr["utLogMap"]["originalPrice"],
        #     "product_discount": itr["utLogMap"]["discount"],
        #     "current_price": itr["utLogMap"]["current_price"],
        #     "product_url": response.urljoin(itr["productUrl"]),
        #     "ratingScore": itr["ratingScore"] if 'ratingScore' in itr.keys() else 0,
        #     "location": itr["location"],
        #     "brandId": itr["brandId"],
        #     "brandName": itr["brandName"],
        #     "sellerId": itr["sellerId"],
        #     "sellerName": itr["sellerName"],
        # }

    def product_detail(self, response):
        body = Selector(text=response.body).css('script').getall()
        body_list = list(filter(lambda k: 'app.run' in k, body))
        body_filter1 = body_list[0].split("app.run")
        body_filter2 = body_filter1[1].split("}}})")
        body_filter3 = body_filter2[0] + "}}})"
        body_filter4 = body_filter3[1:-1]
        json_data = json.loads(body_filter4)
        product_data = json_data["data"]["root"]["fields"] if json_data["data"]["root"]["fields"] else None
        product_average_rating = product_data["review"]["ratings"]["average"] if product_data["review"]["ratings"]["average"] else None
        product_reviews_count = product_data["review"]["ratings"]["reviewCount"] if product_data["review"]["ratings"]["reviewCount"] else None
        product_url = response.url
        product_orignal_price = product_data["skuInfos"]["0"]["price"]["originalPrice"]["value"] if product_data["skuInfos"]["0"]["price"]["originalPrice"]["value"] else None
        product_sale_price = product_data["skuInfos"]["0"]["price"]["salePrice"]["value"] if product_data["skuInfos"]["0"]["price"]["salePrice"]["value"] else None
        product_discount = product_data["skuInfos"]["0"]["price"]["discount"] if product_data["skuInfos"]["0"]["price"]["discount"] else None
        product_image = product_data["skuInfos"]["0"]["dataLayer"]["pdt_photo"] if product_data["skuInfos"]["0"]["dataLayer"]["pdt_photo"] else None
        product_brand = product_data["skuInfos"]["0"]["dataLayer"]["brand_name"] if product_data["skuInfos"]["0"]["dataLayer"]["brand_name"] else None
        product_name = product_data["skuInfos"]["0"]["dataLayer"]["pdt_name"] if product_data["skuInfos"]["0"]["dataLayer"]["pdt_name"] else None
        product_brand_id = product_data["skuInfos"]["0"]["dataLayer"]["brand_id"] if product_data["skuInfos"]["0"]["dataLayer"]["brand_id"] else None
        product_sku = product_data["skuInfos"]["0"]["dataLayer"]["pdt_sku"] if product_data["skuInfos"]["0"]["dataLayer"]["pdt_sku"] else None
        seller_name = product_data["seller"]["name"] if product_data["seller"]["name"] else None
        seller_percentage = product_data["seller"]["percentRate"] if product_data["seller"]["percentRate"] else None
        seller_rate = product_data["seller"]["rate"] if product_data["seller"]["rate"] else None
        seller_rate_level = product_data["seller"]["rateLevel"] if product_data["seller"]["rateLevel"] else None
        seller_seller_id = product_data["seller"]["sellerId"] if product_data["seller"]["sellerId"] else None
        seller_shipment_time = product_data["seller"]["shipOnTime"]["value"] if product_data["seller"]["shipOnTime"]["value"] else None
        seller_url = product_data["seller"]["url"] if product_data["seller"]["url"] else None

        yield {
            "product_average_rating": product_average_rating,
            "product_reviews_count": product_reviews_count,
            "product_url": product_url,
            "product_orignal_price": product_orignal_price,
            "product_sale_price": product_sale_price,
            "product_discount": product_discount,
            "product_image": product_image,
            "product_brand": product_brand,
            "product_name": product_name,
            "product_brand_id": product_brand_id,
            "product_sku": product_sku,
            "seller_name": seller_name,
            "seller_percentage": seller_percentage,
            "seller_rate": seller_rate,
            "seller_rate_level": seller_rate_level,
            "seller_seller_id": seller_seller_id,
            "seller_shipment_time": seller_shipment_time,
            "seller_url": seller_url,
        }
