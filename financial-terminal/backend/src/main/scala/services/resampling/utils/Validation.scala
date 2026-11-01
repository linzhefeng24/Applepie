package services.resampling.utils
import java.time.LocalDate
private[resampling] object Validation:
  def dates(start: String, end: String): Unit =
    try require(!LocalDate.parse(start).isAfter(LocalDate.parse(end)), "开始日期不能晚于结束日期")
    catch
      case _: java.time.format.DateTimeParseException =>
        throw new IllegalArgumentException("日期必须为 YYYY-MM-DD")
