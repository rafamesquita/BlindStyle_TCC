class ClothingItem {
  String? name;
  String? imageUrl;
  String? color;
  String? jsonDescription;

  ClothingItem({this.name, this.imageUrl, this.color, this.jsonDescription});

  factory ClothingItem.fromJson(Map<String, dynamic> json) {
    return ClothingItem(jsonDescription: json['jsonDescription'] ?? '');
  }
}
