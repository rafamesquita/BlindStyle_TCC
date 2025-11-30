import 'dart:ffi';

class CompleteClothingItem {
  String? name;
  String? description;
  String? category;
  String? itemType;
  String? primaryColor;
  String? usage;
  String? texture;
  String? printCategory;
  String? imageUrl;
  bool? ownership;

  CompleteClothingItem({
    this.name,
    this.description,
    this.category,
    this.itemType,
    this.primaryColor,
    this.usage,
    this.texture,
    this.printCategory,
    this.imageUrl,
    this.ownership,
  });

  Map<String, dynamic> toJson() {
    return {
      "name": name ?? "",
      "description": description ?? "",
      "category": category ?? "",
      "item_type": itemType ?? "",
      "primary_color": primaryColor ?? "",
      "usage": usage ?? "",
      "texture": texture ?? "",
      "print_category": printCategory ?? "",
      "image_url": imageUrl ?? "",
      "ownership": ownership ?? true,
    };
  }

  factory CompleteClothingItem.fromJson(Map<String, dynamic> json) {
    return CompleteClothingItem(
      name: json["name"],
      description: json["description"],
      category: json["category"],
      itemType: json["item_type"],
      primaryColor: json["primary_color"],
      usage: json["usage"],
      texture: json["texture"],
      printCategory: json["print_category"],
      imageUrl: json["image_url"],
      ownership: json["ownership"],
    );
  }
}
