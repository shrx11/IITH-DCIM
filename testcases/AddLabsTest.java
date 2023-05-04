import java.io.IOException;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.chrome.ChromeDriver;
import org.testng.annotations.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.support.ui.Select;

public class AddLabsTest {

        public static void main(String[] args) throws IOException, InterruptedException {
                System.setProperty("webdriver.chrome.driver", "/usr/bin/chromedriver");
                ChromeOptions chromeOptions = new ChromeOptions();
                // chromeOptions.addArguments("--headless");
                chromeOptions.addArguments("--no-sandbox");
                chromeOptions.addArguments("--ignore-ssl-errors=yes");
                chromeOptions.addArguments("--ignore-certificate-errors");
                WebDriver driver = new ChromeDriver(chromeOptions);

                driver.get("https://dcim2023.com/login/?next=/");
                Thread.sleep(1000);

                driver.findElement(By.xpath("//input[@name='username']")).sendKeys("admin");
                driver.findElement(By.xpath("//input[@name='password']")).sendKeys("admin@123");
                driver.findElement(By.xpath("//button[@type='submit']")).submit();
                Thread.sleep(2000);

                driver.findElements(By.xpath("//a[@href='/dcim/labs/']")).get(1).click();
                Thread.sleep(3000);

                driver.findElements(By.xpath("//a[@href='/dcim/labs/add/']")).get(1).click();
                Thread.sleep(3000);

                driver.findElement(By.xpath("//input[@name='name']")).sendKeys("C327");
                driver.findElements(By.xpath("//span[@class='ss-arrow']")).get(1).click();
                Thread.sleep(2000);
                driver.findElement(By.xpath("//div[text()='BO']")).click();
               
                driver.findElements(By.xpath("//button[@type='submit']")).get(2).submit();
                Thread.sleep(3000);

                System.out.println("Successfully Lab C327 has been created !!!");
                driver.quit();
        }
}