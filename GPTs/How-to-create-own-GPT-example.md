## 个性化GPT案例：创意天气


Description:

这是一款专门用于创建三维等距插图，在一张图片中同时描绘白天和夜晚的天气的GPT

Instructions:

```
现在你是 "天气艺术家"，这是一款专门用于创建三维等距插图，在一张图片中同时描绘白天和夜晚的天气的GPT。

当我向你提供城市名称时：

1. 请用我提供的Action查询当前天气，如果Action查询失败，请使用内置的web浏览能力去网络搜索城市的天气。
2. 请从你的资料库找出最能代表该城市的特色建筑物或者任何积极正面的标志性物品
3. 请你制作一幅详细的三维等距逼真的 MMORPG 风格插图，分为白天和夜晚两部分，请将API返回的城市的名称和标志性建筑或者物品展示在图中。
4. 根据不同天气显示不同的城市风貌，例如晴天有蓝天白云，如果下雪有雪花和雪人等等
5. 使用清晰的图标和文字显示：
-  温度：注意温度是摄氏度温度，显示时请注明，例如 16°C.
-  天气

你不需要做任何解释，只返回天气结果和城市名称
```

### Actions:

sample API:
```
https://worker-jolly-term-86f5.jimliu.workers.dev/weather?location=beijing
```


## 调用需授权的公开API的案例：图片搜索GPTs

Unsplash 是一个照片共享的网站，摄影师分享很多高清照片，现在创建一个利用这个网站的API获取相应图片资源的GPT

[Unsplash Developer](https://unsplash.com/developers)

``` text
To authenticate requests in this way, pass your application’s access key via the HTTP Authorization header:

Authorization: Client-ID YOUR_ACCESS_KEY
```

测试一下Unsplash的接口
``` shell
curl --location 'https://api.unsplash.com/search/photos?query=apple' \
--header 'Authorization: Client-ID ACCESS_KEY'
```

Photo Search

Description:

Assists in finding photos via Unsplash API

Instructions:

```
When users are looking for some photos, extract the query and user search_photos actions to search and display results.

Please follow the instructions below to display results:
1. Please show top 5 photos from result.
2. The Photo URL displayed should be the URL of the property urls.regular.
3. Display the description.
4. Display the user.name as author.
5. Display the download link.
```

### Actions:

Unsplash API:
```
https://api.unsplash.com/search/photos?query=apple
```

#### 使用GPT4生成OpenAPI schema

``` text
The following is the API call for photo search. Please generate the OpenAPI schema for me.

# 从postman中获得的curl命令
curl --location 'https://api.unsplash.com/search/photos?query=apple' \
--header 'Authorization: Client-ID <ACCESS_KEY>'

# api response
{
    "total": 5,
    "total_pages": 1,
    "results": [
        {
            "id": "CoqJGsFVJtM",
            "slug": "one-red-apple-CoqJGsFVJtM",
            "created_at": "2019-10-12T20:47:23Z",
            "updated_at": "2023-11-20T13:10:24Z",
            "promoted_at": "2019-10-12T21:10:53Z",
            "width": 5209,
            "height": 3473,
            "color": "#262626",
            "blur_hash": "LI9sn~%20yE19tNG-p%MX-ozrXRP",
            "description": "A hand holding an apple",
            "alt_description": "one red apple",
            "breadcrumbs": [
                {
                    "slug": "images",
                    "title": "1,000,000+ Free Images",
                    "index": 0,
                    "type": "landing_page"
                },
                {
                    "slug": "food",
                    "title": "Food Images & Pictures",
                    "index": 1,
                    "type": "landing_page"
                },
                {
                    "slug": "apple",
                    "title": "Apple Images & Photos",
                    "index": 2,
                    "type": "landing_page"
                }
            ],
            "urls": {
                "raw": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?ixid=M3w1MzA4NzJ8MHwxfHNlYXJjaHwxfHxhcHBsZXxlbnwwfHx8fDE3MDA1NTAwODJ8MA&ixlib=rb-4.0.3",
                "full": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w1MzA4NzJ8MHwxfHNlYXJjaHwxfHxhcHBsZXxlbnwwfHx8fDE3MDA1NTAwODJ8MA&ixlib=rb-4.0.3&q=85",
                "regular": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w1MzA4NzJ8MHwxfHNlYXJjaHwxfHxhcHBsZXxlbnwwfHx8fDE3MDA1NTAwODJ8MA&ixlib=rb-4.0.3&q=80&w=1080",
                "small": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w1MzA4NzJ8MHwxfHNlYXJjaHwxfHxhcHBsZXxlbnwwfHx8fDE3MDA1NTAwODJ8MA&ixlib=rb-4.0.3&q=80&w=400",
                "thumb": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w1MzA4NzJ8MHwxfHNlYXJjaHwxfHxhcHBsZXxlbnwwfHx8fDE3MDA1NTAwODJ8MA&ixlib=rb-4.0.3&q=80&w=200",
                "small_s3": "https://s3.us-west-2.amazonaws.com/images.unsplash.com/small/photo-1570913149827-d2ac84ab3f9a"
            },
            "links": {
                "self": "https://api.unsplash.com/photos/one-red-apple-CoqJGsFVJtM",
                "html": "https://unsplash.com/photos/one-red-apple-CoqJGsFVJtM",
                "download": "https://unsplash.com/photos/CoqJGsFVJtM/download?ixid=M3w1MzA4NzJ8MHwxfHNlYXJjaHwxfHxhcHBsZXxlbnwwfHx8fDE3MDA1NTAwODJ8MA",
                "download_location": "https://api.unsplash.com/photos/CoqJGsFVJtM/download?ixid=M3w1MzA4NzJ8MHwxfHNlYXJjaHwxfHxhcHBsZXxlbnwwfHx8fDE3MDA1NTAwODJ8MA"
            },
            "likes": 436,
            "liked_by_user": false,
            "current_user_collections": [],
            "sponsorship": null,
            "topic_submissions": {},
            "user": {
                "id": "vISVsyltI4M",
                "updated_at": "2023-11-21T03:16:22Z",
                "username": "priscilladupreez",
                "name": "Priscilla Du Preez 🇨🇦",
                "first_name": "Priscilla",
                "last_name": "Du Preez 🇨🇦",
                "twitter_username": null,
                "portfolio_url": null,
                "bio": "creating wholesome & modest content for everyone. click on collections for curated content! // if you feel inclined, you can support my work with the link below ♡ ",
                "location": "Lakeland Region, Northern Alberta",
                "links": {
                    "self": "https://api.unsplash.com/users/priscilladupreez",
                    "html": "https://unsplash.com/@priscilladupreez",
                    "photos": "https://api.unsplash.com/users/priscilladupreez/photos",
                    "likes": "https://api.unsplash.com/users/priscilladupreez/likes",
                    "portfolio": "https://api.unsplash.com/users/priscilladupreez/portfolio",
                    "following": "https://api.unsplash.com/users/priscilladupreez/following",
                    "followers": "https://api.unsplash.com/users/priscilladupreez/followers"
                },
                "profile_image": {
                    "small": "https://images.unsplash.com/profile-1695698417767-2297bb54fc4dimage?ixlib=rb-4.0.3&crop=faces&fit=crop&w=32&h=32",
                    "medium": "https://images.unsplash.com/profile-1695698417767-2297bb54fc4dimage?ixlib=rb-4.0.3&crop=faces&fit=crop&w=64&h=64",
                    "large": "https://images.unsplash.com/profile-1695698417767-2297bb54fc4dimage?ixlib=rb-4.0.3&crop=faces&fit=crop&w=128&h=128"
                },
                "instagram_username": "priscilladupreez",
                "total_collections": 28,
                "total_likes": 1121,
                "total_photos": 1278,
                "total_promoted_photos": 654,
                "accepted_tos": true,
                "for_hire": false,
                "social": {
                    "instagram_username": "priscilladupreez",
                    "portfolio_url": null,
                    "twitter_username": null,
                    "paypal_email": null
                }
            },
            "tags": [
                {
                    "type": "landing_page",
                    "title": "apple",
                    "source": {
                        "ancestry": {
                            "type": {
                                "slug": "images",
                                "pretty_slug": "Images"
                            },
                            "category": {
                                "slug": "food",
                                "pretty_slug": "Food"
                            },
                            "subcategory": {
                                "slug": "apple",
                                "pretty_slug": "Apple"
                            }
                        },
                        "title": "Apple images & photos",
                        "subtitle": "Download free apple photos & images",
                        "description": "Choose from a curated selection of apple photos. Always free on Unsplash.",
                        "meta_title": "Apple Pictures [HD] | Download Free Images on Unsplash",
                        "meta_description": "Choose from hundreds of free apple pictures. Download HD apple photos for free on Unsplash.",
                        "cover_photo": {
                            "id": "gDPaDDy6_WE",
                            "slug": "red-apple-fruit-gDPaDDy6_WE",
                            "created_at": "2019-09-17T06:47:55Z",
                            "updated_at": "2023-11-20T10:09:51Z",
                            "promoted_at": null,
                            "width": 6000,
                            "height": 4000,
                            "color": "#c0c0c0",
                            "blur_hash": "LJM%p1t7UGayIoWBa0oLy?j[z;of",
                            "description": "Apple in red ",
                            "alt_description": "red apple fruit",
                            "breadcrumbs": [
                                {
                                    "slug": "images",
                                    "title": "1,000,000+ Free Images",
                                    "index": 0,
                                    "type": "landing_page"
                                },
                                {{
    "total": 5,
    "total_pages": 1,
    "results": [
        {
            "id": "CoqJGsFVJtM",
            "slug": "one-red-apple-CoqJGsFVJtM",
            "created_at": "2019-10-12T20:47:23Z",
            "updated_at": "2023-11-20T13:10:24Z",
            "promoted_at": "2019-10-12T21:10:53Z",
            "width": 5209,
            "height": 3473,
            "color": "#262626",
            "blur_hash": "LI9sn~%20yE19tNG-p%MX-ozrXRP",
            "description": "A hand holding an apple",
            "alt_description": "one red apple",
            "breadcrumbs": [
                {
                    "slug": "images",
                    "title": "1,000,000+ Free Images",
                    "index": 0,
                    "type": "landing_page"
                },
                {
                    "slug": "food",
                    "title": "Food Images & Pictures",
                    "index": 1,
                    "type": "landing_page"
                },
                {
                    "slug": "apple",
                    "title": "Apple Images & Photos",
                    "index": 2,
                    "type": "landing_page"
                }
            ],
            "urls": {
                "raw": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?ixid=M3w1MzA4NzJ8MHwxfHNlYXJjaHwxfHxhcHBsZXxlbnwwfHx8fDE3MDA1NTAwODJ8MA&ixlib=rb-4.0.3",
                "full": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w1MzA4NzJ8MHwxfHNlYXJjaHwxfHxhcHBsZXxlbnwwfHx8fDE3MDA1NTAwODJ8MA&ixlib=rb-4.0.3&q=85",
                "regular": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w1MzA4NzJ8MHwxfHNlYXJjaHwxfHxhcHBsZXxlbnwwfHx8fDE3MDA1NTAwODJ8MA&ixlib=rb-4.0.3&q=80&w=1080",
                "small": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w1MzA4NzJ8MHwxfHNlYXJjaHwxfHxhcHBsZXxlbnwwfHx8fDE3MDA1NTAwODJ8MA&ixlib=rb-4.0.3&q=80&w=400",
                "thumb": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w1MzA4NzJ8MHwxfHNlYXJjaHwxfHxhcHBsZXxlbnwwfHx8fDE3MDA1NTAwODJ8MA&ixlib=rb-4.0.3&q=80&w=200",
                "small_s3": "https://s3.us-west-2.amazonaws.com/images.unsplash.com/small/photo-1570913149827-d2ac84ab3f9a"
            },
            "links": {
                "self": "https://api.unsplash.com/photos/one-red-apple-CoqJGsFVJtM",
                "html": "https://unsplash.com/photos/one-red-apple-CoqJGsFVJtM",
                "download": "https://unsplash.com/photos/CoqJGsFVJtM/download?ixid=M3w1MzA4NzJ8MHwxfHNlYXJjaHwxfHxhcHBsZXxlbnwwfHx8fDE3MDA1NTAwODJ8MA",
                "download_location": "https://api.unsplash.com/photos/CoqJGsFVJtM/download?ixid=M3w1MzA4NzJ8MHwxfHNlYXJjaHwxfHxhcHBsZXxlbnwwfHx8fDE3MDA1NTAwODJ8MA"
            },
            "likes": 436,
            "liked_by_user": false,
            "current_user_collections": [],
            "sponsorship": null,
            "topic_submissions": {},
            "user": {
                "id": "vISVsyltI4M",
                "updated_at": "2023-11-21T03:16:22Z",
                "username": "priscilladupreez",
                "name": "Priscilla Du Preez 🇨🇦",
                "first_name": "Priscilla",
                "last_name": "Du Preez 🇨🇦",
                "twitter_username": null,
                "portfolio_url": null,
                "bio": "creating wholesome & modest content for everyone. click on collections for curated content! // if you feel inclined, you can support my work with the link below ♡ ",
                "location": "Lakeland Region, Northern Alberta",
                "links": {
                    "self": "https://api.unsplash.com/users/priscilladupreez",
                    "html": "https://unsplash.com/@priscilladupreez",
                    "photos": "https://api.unsplash.com/users/priscilladupreez/photos",
                    "likes": "https://api.unsplash.com/users/priscilladupreez/likes",
                    "portfolio": "https://api.unsplash.com/users/priscilladupreez/portfolio",
                    "following": "https://api.unsplash.com/users/priscilladupreez/following",
                    "followers": "https://api.unsplash.com/users/priscilladupreez/followers"
                },
                "profile_image": {
                    "small": "https://images.unsplash.com/profile-1695698417767-2297bb54fc4dimage?ixlib=rb-4.0.3&crop=faces&fit=crop&w=32&h=32",
                    "medium": "https://images.unsplash.com/profile-1695698417767-2297bb54fc4dimage?ixlib=rb-4.0.3&crop=faces&fit=crop&w=64&h=64",
                    "large": "https://images.unsplash.com/profile-1695698417767-2297bb54fc4dimage?ixlib=rb-4.0.3&crop=faces&fit=crop&w=128&h=128"
                },
                "instagram_username": "priscilladupreez",
                "total_collections": 28,
                "total_likes": 1121,
                "total_photos": 1278,
                "total_promoted_photos": 654,
                "accepted_tos": true,
                "for_hire": false,
                "social": {
                    "instagram_username": "priscilladupreez",
                    "portfolio_url": null,
                    "twitter_username": null,
                    "paypal_email": null
                }
            }
        }
    ]
}
```

将生成的json类型的schema拷贝

#### 指定认证方式

Client-ID <ACCESS_KEY>