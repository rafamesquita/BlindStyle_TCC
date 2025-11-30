import 'package:blindstyle/data/services/authentication_service.dart';
import 'package:blindstyle/data/services/item_service.dart';
import 'package:blindstyle/data/services/suggestion_service.dart';
import 'package:blindstyle/stores/authentication_store.dart';
import 'package:blindstyle/stores/item_store.dart';
import 'package:blindstyle/stores/suggestion_store.dart';
import 'package:get_it/get_it.dart';
import '../data/services/description_service.dart';
import '../stores/image_store.dart';
import '../stores/accessibility_store.dart';
import '../stores/history_store.dart';
import '../stores/theme_store.dart';

final getIt = GetIt.instance;

void setupLocator({required String baseUrl}) {
  getIt.registerLazySingleton<DescriptionService>(
    () => DescriptionService(baseUrl: baseUrl),
  );
  getIt.registerLazySingleton<ItemService>(() => ItemService(baseUrl: baseUrl));

  getIt.registerLazySingleton<ImageStore>(
    () => ImageStore(getIt<DescriptionService>(), getIt<AuthenticationStore>()),
  );
  getIt.registerLazySingleton<AuthenticationService>(
    () => AuthenticationService(baseUrl: baseUrl),
  );
  getIt.registerLazySingleton<SuggestionService>(
    () => SuggestionService(baseUrl: baseUrl),
  );

  getIt.registerLazySingleton<AuthenticationStore>(
    () => AuthenticationStore(getIt<AuthenticationService>()),
  );
  getIt.registerSingleton<ThemeStore>(ThemeStore());
  getIt.registerSingleton<AccessibilityStore>(AccessibilityStore());
  getIt.registerSingleton<HistoryStore>(HistoryStore());
  getIt.registerSingleton<ItemStore>(
    ItemStore(getIt<ItemService>(), getIt<AuthenticationStore>()),
  );
  getIt.registerSingleton<SuggestionStore>(
    SuggestionStore(
      getIt<DescriptionService>(),
      getIt<SuggestionService>(),
      getIt<AuthenticationStore>(),
    ),
  );
}
