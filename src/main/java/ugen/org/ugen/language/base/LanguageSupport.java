package ugen.org.ugen.language.base;

public interface LanguageSupport {
    String generateTest(String sourceContent);
    boolean isSourceFile(String filePath);
    boolean isTestFile(String filePath);
    String getTestFilePath(String sourcePath);
    String getTestFramework();
}
