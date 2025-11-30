class ClothingDescription {
  String? description;
  Map<String, dynamic>? jsonDescription;

  ClothingDescription({
    required this.description,
    required this.jsonDescription,
  });

  factory ClothingDescription.fromJson(Map<String, dynamic> json) {
    return ClothingDescription(
      description: json['description'] ?? '',
      jsonDescription:
          json['jsonDescription'] != null
              ? Map<String, dynamic>.from(json['jsonDescription'])
              : {},
    );
  }
}
