# curl https://www.glossier.com/collections/all -o raw/all-us.html
# curl https://www.glossier.com/en-lt/collections/all -o raw/all-lt.html
# curl https://www.glossier.com/en-de/collections/all -o raw/all-de.html

# curl https://www.glossier.com/en-lt/products/futuredew?variant=43781981995253 -o raw/product.html
#  curl https://www.glossier.com/en-lt/products/embroidered-pink-hoodie?variant=48149985624309 -o raw/hoodie.html

#  curl https://www.glossier.com/en-lt/products/balm-dotcom-trio?variant=46731770429685 -o raw/trio_set.html

#  curl https://www.glossier.com/en-lt/products/glossier-you-routine?variant=46634708041973 -o raw/duoroutine_set.html
#  curl https://www.glossier.com/en-lt/products/you-look-good-pet-set?variant=48189058580725 -o raw/ddog_set.html

#  curl https://www.glossier.com/en-lt/products/care-package?variant=46437774426357 -o raw/care_package_out_of_stock.html
#  curl https://www.glossier.com/en-lt/products/glossier-you-soie?variant=47501395853557 -o raw/perfume_some.html

#  curl https://www.glossier.com/en-lt/products/balm-dotcom?parent_collection=balms -o raw/the_balm.html

#  curl https://www.glossier.com/en-lt/products/hand-cream -o raw/out-of-stock-hand-cream.html

#  curl https://www.glossier.com/en-lt/products/the-skincare-icons-eu?variant=48273762582773 -o raw/the-skincare-icons-eu.html

#  curl https://www.glossier.com/en-lt/products/cloud-paint?variant=46178049523957 -o raw/Cloud-Paint-Blush.html
#  curl https://www.glossier.com/en-lt/products/cloud-paint?variant=46178049949941 -o raw/Cloud-Paint-Bronzer.html
# curl https://www.glossier.com/en-lt/products/fragrance-duo -o raw/fragrance-duo.html
# curl https://www.glossier.com/en-lt/products/glossier-you-routine?variant=46634708041973  -o raw/The-Glossier-You-Routine.html

# curl https://www.glossier.com/en-lt/collections/sets -o raw/example-for-claude-from-where-i-grab-the-price-of-the-sets.html

# All 25 sets (LT), from task4/output/sets-scraped.csv. 1 second pause between requests.
mkdir -p raw/sets
curl https://www.glossier.com/en-lt/products/fragrance-duo -o raw/sets/fragrance-duo.html; sleep 1
curl https://www.glossier.com/en-lt/products/the-glossier-icons -o raw/sets/the-glossier-icons.html; sleep 1
curl https://www.glossier.com/en-lt/products/fragrance-trio -o raw/sets/fragrance-trio.html; sleep 1
curl https://www.glossier.com/en-lt/products/fragrance-two-ways -o raw/sets/fragrance-two-ways.html; sleep 1
curl https://www.glossier.com/en-lt/products/balm-dotcom-trio -o raw/sets/balm-dotcom-trio.html; sleep 1
curl https://www.glossier.com/en-lt/products/boy-brow-duo -o raw/sets/boy-brow-duo.html; sleep 1
curl https://www.glossier.com/en-lt/products/travel-spray-balm -o raw/sets/travel-spray-balm.html; sleep 1
curl https://www.glossier.com/en-lt/products/more-of-you-duo -o raw/sets/more-of-you-duo.html; sleep 1
curl https://www.glossier.com/en-lt/products/glossier-you-routine -o raw/sets/glossier-you-routine.html; sleep 1
curl https://www.glossier.com/en-lt/products/in-a-new-york-minute -o raw/sets/in-a-new-york-minute.html; sleep 1
curl https://www.glossier.com/en-lt/products/brow-kit -o raw/sets/brow-kit.html; sleep 1
curl https://www.glossier.com/en-lt/products/lip-kit -o raw/sets/lip-kit.html; sleep 1
curl https://www.glossier.com/en-lt/products/the-cheek-kit -o raw/sets/the-cheek-kit.html; sleep 1
curl https://www.glossier.com/en-lt/products/the-face-kit -o raw/sets/the-face-kit.html; sleep 1
curl https://www.glossier.com/en-lt/products/balm-line-duo -o raw/sets/balm-line-duo.html; sleep 1
curl https://www.glossier.com/en-lt/products/cloud-paint-duo -o raw/sets/cloud-paint-duo.html; sleep 1
curl https://www.glossier.com/en-lt/products/the-no-makeup-makeup-kit -o raw/sets/the-no-makeup-makeup-kit.html; sleep 1
curl https://www.glossier.com/en-lt/products/the-skincare-icons-eu -o raw/sets/the-skincare-icons-eu.html; sleep 1
curl https://www.glossier.com/en-lt/products/you-look-good-pet-set -o raw/sets/you-look-good-pet-set.html; sleep 1
curl https://www.glossier.com/en-lt/products/the-curbside-set -o raw/sets/the-curbside-set.html; sleep 1
curl https://www.glossier.com/en-lt/products/full-body-routine -o raw/sets/full-body-routine.html; sleep 1
curl https://www.glossier.com/en-lt/products/glossier-you-mini-wardrobe -o raw/sets/glossier-you-mini-wardrobe.html; sleep 1
curl https://www.glossier.com/en-lt/products/lash-slick-duo -o raw/sets/lash-slick-duo.html; sleep 1
curl https://www.glossier.com/en-lt/products/ultralip-duo -o raw/sets/ultralip-duo.html; sleep 1
curl https://www.glossier.com/en-lt/products/care-package -o raw/sets/care-package.html