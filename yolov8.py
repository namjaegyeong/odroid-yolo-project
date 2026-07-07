import rclpy

from ros2.image_raw_subscriber import ImageRawSubscriber


def main(args=None):
    rclpy.init(args=args)
    node = ImageRawSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
